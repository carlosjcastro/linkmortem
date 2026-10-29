export const FLICKER_GLSL = `
float flicker(float time, float seed) {
  float wave = sin(time * 1.7 + seed * 20.0) * 0.5 + sin(time * 0.9 + seed * 7.0) * 0.5;
  return smoothstep(-0.4, 0.6, wave);
}
`;
