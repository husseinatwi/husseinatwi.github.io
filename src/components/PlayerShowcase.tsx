import { motion } from "framer-motion";
import { Trophy } from "lucide-react";

const players = [
  {
    name: "Cristiano Ronaldo",
    position: "Forward",
    team: "Al Nassr",
    image:
      "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=400&h=600&fit=crop",
  },
  {
    name: "Lionel Messi",
    position: "Forward",
    team: "Inter Miami",
    image:
      "https://images.unsplash.com/photo-1606925797300-0b35e9d1794e?w=400&h=600&fit=crop",
  },
  {
    name: "Kylian Mbappe",
    position: "Forward",
    team: "Real Madrid",
    image:
      "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=400&h=600&fit=crop",
  },
];

export function PlayerShowcase() {
  return (
    <section className="py-24 px-4 bg-gradient-to-b from-black via-green-950 to-black relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `radial-gradient(circle at 2px 2px, white 1px, transparent 0)`,
            backgroundSize: "40px 40px",
          }}
        />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-6xl font-black text-white mb-4">
            Legendary <span className="text-green-400">Players</span>
          </h2>
          <p className="text-xl text-gray-400">Icons of the beautiful game</p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {players.map((player, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="group relative overflow-hidden rounded-2xl aspect-[3/4] cursor-pointer"
            >
              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent z-10" />
              <img
                src={player.image}
                alt={player.name}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              />
              <div className="absolute bottom-0 left-0 right-0 p-6 z-20">
                <h3 className="text-2xl font-black text-white mb-1">{player.name}</h3>
                <p className="text-green-400 font-semibold">{player.position}</p>
                <p className="text-gray-400 text-sm">{player.team}</p>
              </div>
              <div className="absolute top-4 right-4 w-12 h-12 bg-green-500 rounded-full flex items-center justify-center z-20 opacity-0 group-hover:opacity-100 transition-opacity">
                <Trophy className="w-6 h-6 text-white" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
