import { defineCollection, z } from 'astro:content';

const docs = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    status: z.enum(['active', 'foundational', 'scaffold', 'proposal', 'conjecture', 'experimental']).optional(),
    framework: z.string().optional(),
  }),
});

export const collections = { docs };
