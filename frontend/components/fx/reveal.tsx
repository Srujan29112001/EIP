"use client";

/** Scroll-choreographed reveal — IntersectionObserver adds `.reveal-visible`
 * once (or every entry with `again`). Pure CSS transitions, zero deps. */

import { useEffect, useRef } from "react";

export function Reveal({
  children,
  dir = "up",
  delay = 0,
  again = false,
  className = "",
}: {
  children: React.ReactNode;
  dir?: "up" | "left" | "right" | "scale";
  delay?: number;
  again?: boolean;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            el.classList.add("reveal-visible");
            if (!again) io.disconnect();
          } else if (again) {
            el.classList.remove("reveal-visible");
          }
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -40px 0px" },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [again]);

  return (
    <div
      ref={ref}
      className={`reveal r-${dir} ${className}`}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
    >
      {children}
    </div>
  );
}
