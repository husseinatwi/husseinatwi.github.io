import { motion } from "framer-motion";
import { Calendar } from "lucide-react";
import { cn } from "../lib/utils";

const matches = [
  {
    homeTeam: "Manchester United",
    awayTeam: "Liverpool FC",
    homeScore: 2,
    awayScore: 3,
    date: "Dec 15, 2024",
    status: "Final" as const,
    highlight: true,
  },
  {
    homeTeam: "Real Madrid",
    awayTeam: "Barcelona",
    homeScore: 1,
    awayScore: 1,
    date: "Dec 16, 2024",
    status: "Final" as const,
    highlight: false,
  },
  {
    homeTeam: "Bayern Munich",
    awayTeam: "Borussia Dortmund",
    homeScore: null,
    awayScore: null,
    date: "Dec 20, 2024",
    status: "Upcoming" as const,
    highlight: false,
  },
];

export function FeaturedMatches() {
  return (
    <section className="py-24 px-4 bg-gradient-to-b from-black via-gray-900 to-black">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-6xl font-black text-white mb-4">
            Featured <span className="text-green-400">Matches</span>
          </h2>
          <p className="text-xl text-gray-400">Catch up on the latest action</p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6">
          {matches.map((match, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className={cn(
                "relative p-6 rounded-2xl border backdrop-blur-sm transition-all hover:scale-105 cursor-pointer",
                match.highlight
                  ? "bg-gradient-to-br from-green-500/20 to-emerald-500/20 border-green-500/50"
                  : "bg-white/5 border-white/10 hover:border-white/20"
              )}
            >
              {match.highlight && (
                <div className="absolute top-4 right-4 px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full">
                  FEATURED
                </div>
              )}

              <div className="flex items-center justify-between mb-6">
                <span className="text-sm text-gray-400 flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  {match.date}
                </span>
                <span
                  className={cn(
                    "text-xs font-bold px-3 py-1 rounded-full",
                    match.status === "Final"
                      ? "bg-red-500/20 text-red-400"
                      : "bg-blue-500/20 text-blue-400"
                  )}
                >
                  {match.status}
                </span>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-white font-semibold">{match.homeTeam}</span>
                  <span className="text-3xl font-black text-white">
                    {match.homeScore ?? "-"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-white font-semibold">{match.awayTeam}</span>
                  <span className="text-3xl font-black text-white">
                    {match.awayScore ?? "-"}
                  </span>
                </div>
              </div>

              {match.status === "Final" && (
                <button className="mt-6 w-full py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg font-medium transition-colors">
                  Watch Highlights
                </button>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
