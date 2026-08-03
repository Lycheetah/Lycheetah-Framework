declare module 'node:crypto' {
  export function createHash(algorithm: string): { update(data: string): { digest(encoding: 'hex'): string } };
}
declare module 'node:fs' { const fs: any; export default fs; }
declare module 'node:path' { const path: any; export default path; }
declare module 'node:assert/strict' { const assert: any; export default assert; }
declare const process: { argv: string[]; exit(code?: number): never; stdout: { write(value: string): void } };
