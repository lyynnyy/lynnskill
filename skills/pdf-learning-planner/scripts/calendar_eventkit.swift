import EventKit
import Foundation

enum Mode: String {
    case listSources = "list-sources"
    case ensureCalendar = "ensure-calendar"
    case createEvent = "create-event"
}

let mode = Mode(rawValue: CommandLine.arguments.dropFirst().first ?? "list-sources") ?? .listSources
let store = EKEventStore()
let semaphore = DispatchSemaphore(value: 0)
var granted = false
var authError: Error?

if #available(macOS 14.0, *) {
    store.requestFullAccessToEvents { ok, error in
        granted = ok
        authError = error
        semaphore.signal()
    }
} else {
    store.requestAccess(to: .event) { ok, error in
        granted = ok
        authError = error
        semaphore.signal()
    }
}

semaphore.wait()

guard granted else {
    print("ERROR|Calendar access denied|\(authError?.localizedDescription ?? "unknown")")
    exit(2)
}

func sourceTypeName(_ sourceType: EKSourceType) -> String {
    switch sourceType {
    case .local:
        return "local"
    case .exchange:
        return "exchange"
    case .calDAV:
        return "calDAV"
    case .mobileMe:
        return "mobileMe"
    case .subscribed:
        return "subscribed"
    case .birthdays:
        return "birthdays"
    @unknown default:
        return "unknown"
    }
}

func isCloudCandidate(_ source: EKSource) -> Bool {
    let title = source.title.lowercased()
    return source.sourceType == .calDAV
        || source.sourceType == .mobileMe
        || title.contains("icloud")
        || title.contains("cloud")
}

func printSources() {
    for source in store.sources {
        print("SOURCE|\(source.title)|\(sourceTypeName(source.sourceType))")
        for calendar in source.calendars(for: .event).sorted(by: { $0.title < $1.title }) {
            print("CAL|\(calendar.title)|\(calendar.calendarIdentifier)|\(calendar.allowsContentModifications)")
        }
    }
}

func ensureCalendar(named calendarName: String, preferCloud: Bool) -> (EKSource, EKCalendar) {
    let sources = preferCloud ? store.sources.filter(isCloudCandidate) : store.sources
    guard let source = sources.first(where: { src in
        src.calendars(for: .event).contains(where: { $0.allowsContentModifications })
    }) ?? sources.first else {
        print("ERROR|No usable calendar source found")
        printSources()
        exit(3)
    }

    if let existing = source.calendars(for: .event).first(where: { $0.title == calendarName }) {
        return (source, existing)
    }

    let calendar = EKCalendar(for: .event, eventStore: store)
    calendar.title = calendarName
    calendar.source = source
    do {
        try store.saveCalendar(calendar, commit: true)
        return (source, calendar)
    } catch {
        print("ERROR|Failed to create calendar|\(error.localizedDescription)")
        exit(4)
    }
}

if mode == .listSources {
    printSources()
    exit(0)
}

if mode == .ensureCalendar {
    let args = CommandLine.arguments
    guard args.count >= 3 else {
        print("ERROR|Usage ensure-calendar calendarName [cloud|any]")
        exit(5)
    }
    let calendarName = args[2]
    let preferCloud = args.dropFirst(3).first != "any"
    let (source, calendar) = ensureCalendar(named: calendarName, preferCloud: preferCloud)
    print("CALENDAR|\(calendar.title)|\(calendar.calendarIdentifier)|\(source.title)|\(sourceTypeName(source.sourceType))")
    exit(0)
}

if mode == .createEvent {
    let args = CommandLine.arguments
    guard args.count == 12 else {
        print("ERROR|Usage create-event calendarName title notes url yyyy mm dd hour minute durationMinutes")
        exit(6)
    }

    let calendarName = args[2]
    let title = args[3]
    let notes = args[4]
    let urlString = args[5]
    guard let year = Int(args[6]),
          let month = Int(args[7]),
          let day = Int(args[8]),
          let hour = Int(args[9]),
          let minute = Int(args[10]),
          let durationMinutes = Int(args[11]) else {
        print("ERROR|Invalid date/time arguments")
        exit(7)
    }

    let (source, calendar) = ensureCalendar(named: calendarName, preferCloud: true)
    var components = DateComponents()
    components.calendar = Calendar(identifier: .gregorian)
    components.timeZone = TimeZone.current
    components.year = year
    components.month = month
    components.day = day
    components.hour = hour
    components.minute = minute

    guard let startDate = components.date else {
        print("ERROR|Invalid start date")
        exit(8)
    }

    let event = EKEvent(eventStore: store)
    event.title = title
    event.startDate = startDate
    event.endDate = startDate.addingTimeInterval(TimeInterval(durationMinutes * 60))
    event.isAllDay = false
    event.notes = notes
    event.url = URL(string: urlString)
    event.calendar = calendar

    do {
        try store.save(event, span: .thisEvent, commit: true)
        print("CREATED_EVENT|\(event.calendarItemIdentifier)|\(calendar.calendarIdentifier)|\(source.title)|\(sourceTypeName(source.sourceType))")
    } catch {
        print("ERROR|Failed to create event|\(error.localizedDescription)")
        exit(9)
    }
}
