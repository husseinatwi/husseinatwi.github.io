import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Zap, Globe, Lock, Layers, BarChart3, Wand2 } from "lucide-react";

const features = [
  {
    icon: Wand2,
    title: "AI-Powered Drafts",
    description: "Generate first drafts in seconds. Our AI understands context, tone, and your brand voice.",
  },
  {
    icon: Zap,
    title: "Instant Editing",
    description: "Rewrite, shorten, expand, or change tone with a single click. No more staring at blank pages.",
  },
  {
    icon: Globe,
    title: "30+ Languages",
    description: "Write and translate content in over 30 languages. Reach global audiences effortlessly.",
  },
  {
    icon: Layers,
    title: "Template Library",
    description: "200+ templates for blog posts, ads, emails, social media, and more. Start writing in seconds.",
  },
  {
    icon: Lock,
    title: "Enterprise Security",
    description: "SOC 2 Type II certified. Your data is encrypted at rest and in transit. We never train on your content.",
  },
  {
    icon: BarChart3,
    title: "Content Analytics",
    description: "Track readability scores, SEO metrics, and engagement predictions before you publish.",
  },
];

export function Features() {
  return (
    <section id="features" className="py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Everything you need to create amazing content
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Powerful features that help your team write better, faster, and more consistently.
          </p>
        </div>
        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title} className="border-border/50 transition-colors hover:border-border hover:shadow-md">
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <feature.icon className="h-5 w-5 text-primary" />
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
                <CardDescription className="text-sm leading-relaxed">
                  {feature.description}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
