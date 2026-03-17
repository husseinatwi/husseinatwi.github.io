import { Card, CardContent } from "@/components/ui/card";

const testimonials = [
  {
    quote: "Nexus AI cut our content production time by 80%. We went from publishing 4 blog posts a month to 20.",
    name: "Sarah Chen",
    role: "Head of Content, TechCorp",
  },
  {
    quote: "The quality of AI-generated drafts is incredible. It truly understands our brand voice after just a few examples.",
    name: "Marcus Johnson",
    role: "Marketing Director, ScaleUp",
  },
  {
    quote: "We use Nexus AI for everything — emails, landing pages, documentation. It's become indispensable for our team.",
    name: "Emily Rodriguez",
    role: "VP of Marketing, CloudBase",
  },
];

export function Testimonials() {
  return (
    <section id="testimonials" className="bg-muted/30 py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Loved by content teams everywhere
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            See what our customers have to say about Nexus AI.
          </p>
        </div>
        <div className="mt-16 grid gap-8 md:grid-cols-3">
          {testimonials.map((t) => (
            <Card key={t.name} className="border-border/50">
              <CardContent className="pt-6">
                <p className="text-sm leading-relaxed text-foreground/80">
                  &ldquo;{t.quote}&rdquo;
                </p>
                <div className="mt-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                    {t.name[0]}
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{t.name}</p>
                    <p className="text-xs text-muted-foreground">{t.role}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
