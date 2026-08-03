import fs from 'node:fs';
import path from 'node:path';
import { analyzeText } from './text-adapter.ts';
import { scoreStructuredAssessment } from './structured.ts';

function read(pathname: string): string {
  return fs.readFileSync(path.resolve(pathname), 'utf8');
}

function usage(): never {
  console.error(`Usage:
  node --experimental-strip-types src/cli.ts analyze-text <text-file>
  node --experimental-strip-types src/cli.ts score <assessment.json>
  node --experimental-strip-types src/cli.ts corpus <corpus.jsonl> [output.jsonl]`);
  process.exit(2);
}

const [command, input, output] = process.argv.slice(2);
if (!command || !input) usage();

if (command === 'analyze-text') {
  console.log(JSON.stringify(analyzeText(read(input)), null, 2));
} else if (command === 'score') {
  console.log(JSON.stringify(scoreStructuredAssessment(JSON.parse(read(input))), null, 2));
} else if (command === 'corpus') {
  const lines = read(input).split(/\r?\n/).filter(Boolean);
  const results = lines.map(line => {
    const item = JSON.parse(line);
    return { id: item.id, family: item.family, title: item.title, result: analyzeText(item.text) };
  });
  const rendered = results.map(x => JSON.stringify(x)).join('\n') + '\n';
  if (output) fs.writeFileSync(path.resolve(output), rendered);
  else process.stdout.write(rendered);
} else {
  usage();
}
