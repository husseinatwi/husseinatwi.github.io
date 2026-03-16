import { SoccerHero } from "./components/SoccerHero";
import { FeaturedMatches } from "./components/FeaturedMatches";
import { PlayerShowcase } from "./components/PlayerShowcase";
import { StatsSection } from "./components/StatsSection";
import { Newsletter } from "./components/Newsletter";
import { Footer } from "./components/Footer";

export default function App() {
  return (
    <div className="min-h-screen bg-black">
      <SoccerHero />
      <FeaturedMatches />
      <PlayerShowcase />
      <StatsSection />
      <Newsletter />
      <Footer />
    </div>
  );
}
