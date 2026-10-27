import { useContext } from "react";
import { MotionContext } from "./MotionProvider";

export function useMotion() {
  const state = useContext(MotionContext);
  if (!state) throw new Error("useMotion must be used inside MotionProvider");
  return state;
}
