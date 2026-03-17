"use client";

import { motion, useReducedMotion } from "framer-motion";
import { useState, useEffect } from "react";
import {
  Check,
  Star,
  Users,
  Award,
  TrendingUp,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface TextGenerateEffectProps {
  words: string;
  className?: string;
  filter?: boolean;
  duration?: number;
}

const TextGenerateEffect = ({
  words,
  className,
  filter = true,
  duration = 0.5,
}: TextGenerateEffectProps) => {
  const [scope, setScope] = useState<HTMLDivElement | null>(null);
  const wordsArray = words.split(" ");

  useEffect(() => {
    if (!scope) return;

    const spans = scope.querySelectorAll("span");
    spans.forEach((span, idx) => {
      setTimeout(() => {
        span.style.opacity = "1";
        span.style.filter = filter ? "blur(0px)" : "none";
      }, idx * 200);
    });
  }, [scope, filter]);

  return (
    <div className={cn("font-bold", className)}>
      <div className="mt-4">
        <div
          ref={setScope}
          className="text-foreground text-2xl leading-snug tracking-wide"
        >
          {wordsArray.map((word, idx) => (
            <span
              key={word + idx}
              className="opacity-0 inline-block"
              style={{
                filter: filter ? "blur(10px)" : "none",
                transition: `opacity ${duration}s, filter ${duration}s`,
              }}
            >
              {word}{" "}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

interface Testimonial {
  name: string;
  role: string;
  content: string;
  rating: number;
  image: string;
}

interface CoachFunnelProps {
  coachName?: string;
  coachTitle?: string;
  coachImage?: string;
  heroText?: string;
  ctaText?: string;
  testimonials?: Testimonial[];
  enableAnimations?: boolean;
}

const defaultTestimonials: Testimonial[] = [
  {
    name: "أحمد محمد",
    role: "رائد أعمال",
    content:
      "تغيرت حياتي بالكامل بعد العمل مع هذا المدرب. النتائج كانت مذهلة!",
    rating: 5,
    image:
      "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop",
  },
  {
    name: "فاطمة علي",
    role: "مديرة تنفيذية",
    content: "أفضل استثمار قمت به في نفسي. الجلسات كانت تحويلية حقاً",
    rating: 5,
    image:
      "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop",
  },
  {
    name: "خالد السعيد",
    role: "مستشار مالي",
    content: "منهجية واضحة ونتائج ملموسة. أنصح الجميع بهذه التجربة",
    rating: 5,
    image:
      "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop",
  },
];

export function ArabCoachFunnel({
  coachName = "د. محمد العربي",
  coachTitle = "مدرب تطوير الذات والقيادة",
  coachImage = "https://images.unsplash.com/photo-1556157382-97eda2d62296?w=400&h=400&fit=crop",
  heroText = "حول حياتك من العادية إلى الاستثنائية في 90 يوماً فقط",
  ctaText = "احجز استشارتك المجانية الآن",
  testimonials = defaultTestimonials,
  enableAnimations = true,
}: CoachFunnelProps) {
  const shouldReduceMotion = useReducedMotion();
  const shouldAnimate = enableAnimations && !shouldReduceMotion;
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 25,
      },
    },
  };

  const stats = [
    { icon: Users, value: "+500", label: "عميل راضٍ" },
    { icon: Award, value: "15+", label: "سنة خبرة" },
    { icon: TrendingUp, value: "98%", label: "نسبة نجاح" },
    { icon: Clock, value: "24/7", label: "دعم مستمر" },
  ];

  const benefits = [
    "برنامج مخصص يناسب احتياجاتك الشخصية",
    "جلسات فردية مع المدرب مباشرة",
    "أدوات وموارد حصرية للتطوير",
    "متابعة مستمرة وتقييم دوري",
    "مجتمع داعم من المتدربين",
    "ضمان استرجاع المال خلال 30 يوم",
  ];

  return (
    <div
      className="min-h-screen w-full bg-gradient-to-br from-background via-background to-muted"
      dir="rtl"
    >
      <motion.div
        variants={shouldAnimate ? containerVariants : {}}
        initial={shouldAnimate ? "hidden" : "visible"}
        animate={isVisible ? "visible" : "hidden"}
        className="w-full"
      >
        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center px-4 py-20 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />

          <div className="container mx-auto max-w-7xl relative z-10">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              {/* Right Side - Content */}
              <motion.div
                variants={shouldAnimate ? itemVariants : {}}
                className="space-y-8 text-center lg:text-right"
              >
                <motion.div
                  initial={shouldAnimate ? { scale: 0.8, opacity: 0 } : {}}
                  animate={shouldAnimate ? { scale: 1, opacity: 1 } : {}}
                  transition={shouldAnimate ? { delay: 0.3, type: "spring" } : {}}
                  className="inline-block"
                >
                  <span className="bg-primary/10 text-primary px-6 py-2 rounded-full text-sm font-semibold">
                    ✨ عرض محدود لفترة قصيرة
                  </span>
                </motion.div>

                <h1 className="text-5xl md:text-7xl font-black text-foreground leading-tight">
                  {heroText}
                </h1>

                <TextGenerateEffect
                  words="اكتشف إمكانياتك الحقيقية وحقق أهدافك مع برنامج تدريبي شامل ومخصص"
                  className="text-xl md:text-2xl text-muted-foreground font-normal"
                  duration={0.8}
                />

                <motion.div
                  variants={shouldAnimate ? itemVariants : {}}
                  className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-end"
                >
                  <motion.button
                    whileHover={shouldAnimate ? { scale: 1.05, y: -2 } : {}}
                    whileTap={shouldAnimate ? { scale: 0.98 } : {}}
                    className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-4 rounded-lg font-bold text-lg shadow-lg shadow-primary/25 transition-all"
                  >
                    {ctaText}
                  </motion.button>
                  <motion.button
                    whileHover={shouldAnimate ? { scale: 1.05 } : {}}
                    whileTap={shouldAnimate ? { scale: 0.98 } : {}}
                    className="border-2 border-border hover:bg-muted px-8 py-4 rounded-lg font-bold text-lg transition-all"
                  >
                    شاهد الفيديو التعريفي
                  </motion.button>
                </motion.div>

                {/* Stats */}
                <motion.div
                  variants={shouldAnimate ? itemVariants : {}}
                  className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-8"
                >
                  {stats.map((stat, idx) => (
                    <motion.div
                      key={stat.label}
                      initial={shouldAnimate ? { opacity: 0, y: 20 } : {}}
                      animate={shouldAnimate ? { opacity: 1, y: 0 } : {}}
                      transition={
                        shouldAnimate ? { delay: 0.5 + idx * 0.1 } : {}
                      }
                      className="text-center"
                    >
                      <stat.icon className="w-8 h-8 mx-auto mb-2 text-primary" />
                      <div className="text-3xl font-bold text-foreground">
                        {stat.value}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {stat.label}
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              </motion.div>

              {/* Left Side - Coach Image */}
              <motion.div
                variants={shouldAnimate ? itemVariants : {}}
                className="relative"
              >
                <motion.div
                  initial={shouldAnimate ? { scale: 0.8, opacity: 0 } : {}}
                  animate={shouldAnimate ? { scale: 1, opacity: 1 } : {}}
                  transition={
                    shouldAnimate ? { delay: 0.4, type: "spring" } : {}
                  }
                  className="relative"
                >
                  <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-transparent rounded-3xl blur-3xl" />
                  <img
                    src={coachImage}
                    alt={coachName}
                    className="relative rounded-3xl shadow-2xl w-full max-w-md mx-auto"
                  />
                  <div className="absolute bottom-8 right-8 bg-card/95 backdrop-blur-sm p-6 rounded-2xl shadow-xl border border-border">
                    <h3 className="text-2xl font-bold text-foreground mb-1">
                      {coachName}
                    </h3>
                    <p className="text-muted-foreground">{coachTitle}</p>
                    <div className="flex items-center gap-1 mt-2">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className="w-4 h-4 fill-yellow-400 text-yellow-400"
                        />
                      ))}
                      <span className="mr-2 text-sm text-muted-foreground">
                        (500+ تقييم)
                      </span>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-20 px-4 bg-muted/30">
          <div className="container mx-auto max-w-6xl">
            <motion.div
              variants={shouldAnimate ? itemVariants : {}}
              className="text-center mb-16"
            >
              <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
                ماذا ستحصل عليه؟
              </h2>
              <p className="text-xl text-muted-foreground">
                برنامج شامل مصمم خصيصاً لتحقيق أهدافك
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-6">
              {benefits.map((benefit, idx) => (
                <motion.div
                  key={idx}
                  initial={shouldAnimate ? { opacity: 0, x: 20 } : {}}
                  animate={shouldAnimate ? { opacity: 1, x: 0 } : {}}
                  transition={
                    shouldAnimate ? { delay: 0.6 + idx * 0.1 } : {}
                  }
                  whileHover={shouldAnimate ? { scale: 1.02, x: -5 } : {}}
                  className="flex items-start gap-4 bg-card p-6 rounded-xl border border-border shadow-sm hover:shadow-md transition-all"
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                    <Check className="w-5 h-5 text-primary" />
                  </div>
                  <p className="text-lg text-foreground">{benefit}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="py-20 px-4">
          <div className="container mx-auto max-w-6xl">
            <motion.div
              variants={shouldAnimate ? itemVariants : {}}
              className="text-center mb-16"
            >
              <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
                قصص نجاح عملائنا
              </h2>
              <p className="text-xl text-muted-foreground">
                اكتشف كيف غيّر برنامجنا حياة المئات
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {testimonials.map((testimonial, idx) => (
                <motion.div
                  key={idx}
                  initial={shouldAnimate ? { opacity: 0, y: 30 } : {}}
                  animate={shouldAnimate ? { opacity: 1, y: 0 } : {}}
                  transition={
                    shouldAnimate ? { delay: 0.8 + idx * 0.15 } : {}
                  }
                  whileHover={shouldAnimate ? { y: -8 } : {}}
                  className="bg-card p-8 rounded-2xl border border-border shadow-lg hover:shadow-xl transition-all"
                >
                  <div className="flex items-center gap-4 mb-4">
                    <img
                      src={testimonial.image}
                      alt={testimonial.name}
                      className="w-16 h-16 rounded-full object-cover"
                    />
                    <div>
                      <h4 className="font-bold text-foreground">
                        {testimonial.name}
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        {testimonial.role}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star
                        key={i}
                        className="w-4 h-4 fill-yellow-400 text-yellow-400"
                      />
                    ))}
                  </div>
                  <p className="text-muted-foreground leading-relaxed">
                    {testimonial.content}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Final CTA Section */}
        <section className="py-20 px-4 bg-gradient-to-br from-primary/10 via-primary/5 to-transparent">
          <div className="container mx-auto max-w-4xl text-center">
            <motion.div
              variants={shouldAnimate ? itemVariants : {}}
              className="space-y-8"
            >
              <h2 className="text-4xl md:text-6xl font-bold text-foreground">
                هل أنت مستعد للتغيير؟
              </h2>
              <p className="text-xl md:text-2xl text-muted-foreground">
                انضم إلى مئات الأشخاص الذين حققوا أهدافهم معنا
              </p>

              <motion.div
                whileHover={shouldAnimate ? { scale: 1.05 } : {}}
                whileTap={shouldAnimate ? { scale: 0.98 } : {}}
                className="inline-block"
              >
                <button className="bg-primary hover:bg-primary/90 text-primary-foreground px-12 py-6 rounded-xl font-bold text-2xl shadow-2xl shadow-primary/30 transition-all">
                  ابدأ رحلتك الآن
                </button>
              </motion.div>

              <div className="flex items-center justify-center gap-8 pt-8 text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Check className="w-5 h-5 text-primary" />
                  <span>بدون التزام طويل الأمد</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-5 h-5 text-primary" />
                  <span>ضمان استرجاع المال</span>
                </div>
              </div>
            </motion.div>
          </div>
        </section>
      </motion.div>
    </div>
  );
}
