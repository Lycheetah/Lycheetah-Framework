import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const toolDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(toolDir);
const listeningDir = path.join(root, 'LISTENING');

const firstSource = fs.readFileSync(
  path.join(root, '01_THE_DOOR_THAT_REMEMBERED.md'),
  'utf8',
);
const secondSource = fs.readFileSync(
  path.join(root, '02_THE_BELL_BENEATH_THE_SCHOOL.md'),
  'utf8',
);
const thirdSource = fs.readFileSync(
  path.join(root, '03_THE_ROAD_THAT_COUNTED_THE_LIVING.md'),
  'utf8',
);

function fromHeading(source, heading) {
  const start = source.indexOf(heading);
  if (start === -1) {
    throw new Error(`Missing listening-edition start heading: ${heading}`);
  }
  return source.slice(start);
}

function cleanForListening(source) {
  return source
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/^---\s*$/gm, '')
    .replace(/\*\*/g, '')
    .replace(/(?<!\*)\*(?!\*)/g, '')
    .replace(/^⊚$/gm, 'A circle with a point at its centre.')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

const title = [
  'THE BOOK OF THE LONG LIGHT',
  'Volume One: The Door That Remembered',
  '',
].join('\n');

const openingBody = cleanForListening(fromHeading(firstSource, '## PROLOGUE'));
const chapterFourBody = cleanForListening(
  fromHeading(secondSource, '## CHAPTER FOUR'),
);
const chapterFiveBody = cleanForListening(
  fromHeading(thirdSource, '## CHAPTER FIVE'),
);

const opening = `${title}${openingBody}\n`;
const chapterFour = `${title}Second Movement\n\n${chapterFourBody}\n`;
const chapterFive = `${title}Third Movement\n\n${chapterFiveBody}\n`;
const continuous = [
  title.trim(),
  openingBody,
  chapterFourBody,
  chapterFiveBody,
  '',
].join('\n\n');

fs.mkdirSync(listeningDir, { recursive: true });
fs.writeFileSync(
  path.join(listeningDir, '01_OPENING_MOVEMENT.txt'),
  opening,
  'utf8',
);
fs.writeFileSync(
  path.join(listeningDir, '02_THE_BELL_BENEATH_THE_SCHOOL.txt'),
  chapterFour,
  'utf8',
);
fs.writeFileSync(
  path.join(listeningDir, '03_THE_ROAD_THAT_COUNTED_THE_LIVING.txt'),
  chapterFive,
  'utf8',
);
fs.writeFileSync(
  path.join(listeningDir, 'THE_BOOK_OF_THE_LONG_LIGHT_NIGHT_EDITION.txt'),
  continuous,
  'utf8',
);

console.log('Built four listening files.');
