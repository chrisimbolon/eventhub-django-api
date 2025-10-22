import { EventCard } from "./EventCard";

export function EventGrid({ events }: { events: any[] }) {
  if (!events.length) {
    return (
      <div className="text-center text-gray-500 mt-16">
        <p className="text-lg">No events yet 🎤</p>
        <p className="text-sm">Try creating your first event!</p>
      </div>
    );
  }

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-8">
      {events.map((event) => (
        <EventCard key={event.id} event={event} />
      ))}
    </div>
  );
}
