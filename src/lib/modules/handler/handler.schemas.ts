import z from 'zod';

export const HandlerSchema = z.object({
	id: z.string(),
	userId: z.string(),
	filePath: z.string(),
	fileName: z.string(),
	runtime: z.enum(['python', 'typescript', 'javascript']),
	async: z.boolean().default(false),
	name: z.string(),
	enabled: z.boolean().default(true),
	createdAt: z.date(),
	updatedAt: z.date()
});

export const HandlerCreateSchema = HandlerSchema.omit({
	id: true,
	createdAt: true,
	updatedAt: true
});

export const HandlerCreatePreflightSchema = HandlerCreateSchema.pick({
	runtime: true,
	async: true,
	name: true
}).extend({
	file: z.file()
});

export const HandlerUpdateSchema = HandlerSchema.pick({
	id: true,
	name: true,
	async: true,
	enabled: true
});
