// src/components/package-detail/ItinerarySection.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// Buat interface untuk itinerary
interface ItineraryDay {
  day: number;
  title: string;
  description: string;
}

// Buat data dummy
const dummyItinerary: ItineraryDay[] = [
  {
    day: 1,
    title: "Keberangkatan dari Jakarta",
    description:
      "Jamaah berkumpul di bandara Soekarno-Hatta 3 jam sebelum keberangkatan untuk proses check-in dan imigrasi.",
  },
  {
    day: 2,
    title: "Tiba di Jeddah",
    description:
      "Tiba di bandara Jeddah, dilanjutkan dengan city tour dan miqat di Bir Ali.",
  },
  {
    day: 3,
    title: "Masuk ke Mekkah",
    description:
      "Persiapan memasuki Mekkah, check-in hotel, dan melaksanakan umrah pertama kali.",
  },
  // ... tambahkan hari-hari lainnya
];

export const ItinerarySection = () => {
  return (
    <section>
      <h2 className="text-3xl font-bold text-center mb-8">
        Rincian Perjalanan
      </h2>
      <div className="space-y-4">
        {dummyItinerary.map((day) => (
          <Card key={day.day} className="overflow-hidden">
            <CardHeader>
              <CardTitle>
                Hari ke-{day.day}: {day.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p>{day.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
};
