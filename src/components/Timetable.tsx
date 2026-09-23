import { CalendarDays, Clock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const lessons = [
  { day: 'Lundi', subject: 'PCT', start: '18:00', end: '20:00' },
  { day: 'Jeudi', subject: 'PCT', start: '18:00', end: '20:00' },
]

export function Timetable() {
  return (
    <section aria-labelledby="timetable-title" className="mx-auto max-w-7xl px-5 pb-10 lg:px-8">
      <div className="mb-6 flex items-center gap-3">
        <CalendarDays aria-hidden="true" className="size-6 text-primary" />
        <h2 id="timetable-title" className="font-serif text-3xl">Emploi du temps</h2>
      </div>
      <p className="mb-6 text-sm text-muted-foreground">Chaque semaine</p>
      <ul className="grid gap-5 sm:grid-cols-2">
        {lessons.map((lesson) => (
          <li key={lesson.day}>
            <Card>
              <CardHeader>
                <p className="text-sm font-medium text-primary">{lesson.day}</p>
                <CardTitle className="font-serif text-xl">{lesson.subject}</CardTitle>
                <p className="text-sm text-muted-foreground">Professeur : Mr KPANDJAO</p>
              </CardHeader>
              <CardContent>
                <p className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock aria-hidden="true" className="size-4" />
                  <span><time dateTime={lesson.start}>18 h</time> – <time dateTime={lesson.end}>20 h</time></span>
                </p>
              </CardContent>
            </Card>
          </li>
        ))}
      </ul>
      <a
        href="/emploi-du-temps-pct.pdf"
        download
        className="mt-6 inline-flex rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
      >
        Télécharger l’emploi du temps (PDF)
      </a>
    </section>
  )
}
