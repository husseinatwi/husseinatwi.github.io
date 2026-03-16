import { motion } from "framer-motion";
import { Users, Trophy, Calendar, Play } from "lucide-react";
import { cn } from "../lib/utils";

const stats = [
  { icon: Users, label: "Active Players", value: "5,000+", color: "from-blue-500 to-cyan-500" },
  { icon: Trophy, label: "Championships", value: "150+", color: "from-yellow-500 to-orange-500" },
  { icon: Calendar, label: "Matches Played", value: "1,200+", color: "from-green-500 to-emerald-500" },
  { icon: Play, label: "Hours Watched", value: "50K+", color: "from-purple-500 to-pink-500" },
];

export function StatsSection() {
  return (
    <section className="py-24 px-4 bg-black">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="relative group"
            >
              <div className="p-8 rounded-2xl bg-gradient-to-br from-white/5 to-white/10 border border-white/10 backdrop-blur-sm hover:border-white/20 transition-all">
                <div
                  className={cn(
                    "w-16 h-16 rounded-full bg-gradient-to-br mb-6 flex items-center justify-center",
                    stat.color
                  )}
                >
                  <stat.icon className="w-8 h-8 text-white" />
                </div>
                <div className="text-5xl font-black text-white mb-2">{stat.value}</div>
                <div className="text-gray-400 font-medium">{stat.label}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
