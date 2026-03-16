import { motion } from "framer-motion";

export function Newsletter() {
  return (
    <section className="py-24 px-4 bg-gradient-to-br from-green-900 via-emerald-800 to-green-900 relative overflow-hidden">
      <div className="absolute inset-0 opacity-20">
        {Array.from({ length: 50 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0.2, 0.8, 0.2],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      <div className="max-w-4xl mx-auto text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
            Stay in the Game
          </h2>
          <p className="text-xl text-white/80 mb-10">
            Get the latest news, match updates, and exclusive content delivered to your
            inbox
          </p>
          <div className="flex flex-col sm:flex-row gap-4 max-w-2xl mx-auto">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-6 py-4 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white placeholder:text-white/50 focus:outline-none focus:border-white/40"
            />
            <button className="px-8 py-4 bg-white text-green-900 rounded-full font-bold hover:scale-105 transition-transform">
              Subscribe
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
