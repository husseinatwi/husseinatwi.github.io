export function LogoCloud() {
  const companies = [
    "Stripe", "Vercel", "Shopify", "Notion", "Linear", "Figma"
  ];

  return (
    <section className="border-y border-border/40 bg-muted/30 py-12">
      <div className="mx-auto max-w-6xl px-6">
        <p className="text-center text-sm font-medium text-muted-foreground">
          Trusted by 10,000+ teams at companies like
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
          {companies.map((name) => (
            <span
              key={name}
              className="text-xl font-bold tracking-tight text-muted-foreground/50"
            >
              {name}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
