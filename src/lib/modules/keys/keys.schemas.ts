import z from 'zod';

export const KeysSchemas = z.object({
	id: z.string(),
	userId: z.string(),
	name: z.string().min(1).max(100),
	accessType: z.enum(['FULL', 'SCOPED']),
	prefix: z.string().min(1).max(7),
	secretKey: z.string().min(32).max(64),
	createdAt: z.date(),
	updatedAt: z.date(),
	revokedAt: z.date().nullable().optional()
});

export const KeyCreateSchema = KeysSchemas.omit({
	id: true,
	createdAt: true,
	updatedAt: true,
	revokedAt: true
});

export const KeyCreatePreflightSchema = KeyCreateSchema.pick({
	name: true
});
