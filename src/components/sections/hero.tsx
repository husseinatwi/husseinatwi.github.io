import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Play } from "lucide-react";

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background" />
      <div className="mx-auto max-w-6xl px-6 pb-24 pt-32 text-center">
        <Badge variant="secondary" className="mb-6 px-4 py-1.5 text-sm font-medium">
          Now in Public Beta
        </Badge>
        <h1 className="mx-auto max-w-4xl text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
          Write smarter.{" "}
          <span className="bg-gradient-to-r from-chart-1 to-chart-3 bg-clip-text text-transparent">
            Ship faster.
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
          Nexus AI is the writing assistant your team has been waiting for. Generate blog posts,
          marketing copy, and product documentation in seconds — not hours.
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <Button size="lg" className="gap-2 px-8 text-base">
            Start Free Trial
            <ArrowRight className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="lg" className="gap-2 px-8 text-base">
            <Play className="h-4 w-4" />
            Watch Demo
          </Button>
        </div>
        <p className="mt-4 text-sm text-muted-foreground">
          No credit card required. 14-day free trial.
        </p>

        {/* Hero visual */}
        <div className="mx-auto mt-16 max-w-4xl overflow-hidden rounded-xl border border-border/50 bg-card shadow-2xl shadow-primary/5">
          <div className="flex items-center gap-2 border-b border-border/50 bg-muted/50 px-4 py-3">
            <div className="h-3 w-3 rounded-full bg-red-400" />
            <div className="h-3 w-3 rounded-full bg-yellow-400" />
            <div className="h-3 w-3 rounded-full bg-green-400" />
            <span className="ml-2 text-xs text-muted-foreground">nexus-editor.tsx</span>
          </div>
          <div className="p-8 text-left">
            <div className="space-y-3">
              <div className="h-4 w-3/4 rounded bg-muted animate-pulse" />
              <div className="h-4 w-full rounded bg-muted animate-pulse [animation-delay:150ms]" />
              <div className="h-4 w-5/6 rounded bg-muted animate-pulse [animation-delay:300ms]" />
              <div className="h-4 w-2/3 rounded bg-primary/20 animate-pulse [animation-delay:450ms]" />
              <div className="mt-6 h-4 w-full rounded bg-muted animate-pulse [animation-delay:600ms]" />
              <div className="h-4 w-4/5 rounded bg-muted animate-pulse [animation-delay:750ms]" />
              <div className="h-4 w-3/4 rounded bg-primary/20 animate-pulse [animation-delay:900ms]" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
