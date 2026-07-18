"use client";

/** Cipher-scramble text — glyphs decode left-to-right into the real string.
 * Runs once on mount; instant under reduced motion. */

import { useEffect, useRef, useState } from "react";

const GLYPHS = "◈◇▲△⟠01!<>_/\\[]{}#$%&*ΞΔΣΨΩ";

export function ScrambleText({
  text,
  speed = 28,
  className = "",
}: {
  text: string;
  speed?: number;
  className?: string;
}) {
  const [out, setOut] = useState(text);
  const done = useRef(false);

  useEffect(() => {
    if (done.current) return;
    done.current = true;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setOut(text);
      return;
    }
    let frame = 0;
    const id = setInterval(() => {
      frame += 1;
      const settled = Math.floor(frame / 2.2);
      setOut(
        text
          .split("")
          .map((ch, i) => {
            if (ch === " " || i < settled) return ch;
            return GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
          })
          .join(""),
      );
      if (settled >= text.length) clearInterval(id);
    }, speed);
    return () => clearInterval(id);
  }, [text, speed]);

  return <span className={className} aria-label={text}>{out}</span>;
}
