import { config } from "@remotion/eslint-config-flat";

export default [
  ...config,
  { rules: { "@typescript-eslint/no-explicit-any": "off" } },
];
