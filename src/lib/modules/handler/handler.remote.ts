import { command, form, query } from '$app/server';
import { mkdir, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { HandlerCreatePreflightSchema, HandlerCreateSchema } from './handler.schemas';
import { env } from '$env/dynamic/private';
import z from 'zod';
import { redirect } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { handler } from '$lib/server/db/schema';
import { and, desc, eq, isNull } from 'drizzle-orm';
import { checkAuthenticated } from '$lib/server/db/utils';
import { UPLOAD_PATH } from '$env/static/private';

type Runtime = 'python' | 'typescript' | 'javascript';
const RUNTIMES = new Map<string, Runtime>([
	['py', 'python'],
	['ts', 'typescript'],
	['js', 'javascript']
]);

const checkRuntime = (fileName: string) => {
	const fileNameInDots = fileName.split('.');

	const extension = fileNameInDots[fileNameInDots.length - 1];

	return {
		extension,
		runtime: RUNTIMES.get(extension)
	};
};

export const createHandler = form(HandlerCreatePreflightSchema, async (data) => {
	const user = await checkAuthenticated();

	if (!user) redirect(303, '/auth/signin');

	const handlerContent = await data.file.text();
	const uuid = crypto.randomUUID();

	const runtime = checkRuntime(data.file.name);

	if (!runtime.runtime) {
		console.error('Unsupported file extension:', runtime.extension);
		return redirect(303, '/app/handler');
	}

	const fileName = `${uuid}.${runtime.extension}`;
	const filePath = `${env.UPLOAD_PATH}/${fileName}`;

	const newHandler: z.infer<typeof HandlerCreateSchema> = {
		async: data.async,
		enabled: true,
		name: data.name,
		runtime: runtime.runtime,
		fileName,
		filePath,
		userId: user.id
	};

	const safeData = HandlerCreateSchema.safeParse(newHandler);
	if (!safeData.success) {
		console.error('Validation error creating handler:', safeData.error);
		return redirect(303, '/app/handler');
	}

	if (!existsSync(UPLOAD_PATH)) {
		await mkdir(UPLOAD_PATH, { recursive: true });
	}

	await writeFile(filePath, handlerContent);

	await db.insert(handler).values({
		...safeData.data,
		id: crypto.randomUUID()
	});

	redirect(303, '/app/handler');
});

export const getHandlers = query(async () => {
	const user = await checkAuthenticated();

	if (!user) redirect(303, '/auth/signin');

	const handlers = await db
		.select()
		.from(handler)
		.where(and(eq(handler.userId, user.id), isNull(handler.deletedAt)))
		.orderBy(desc(handler.createdAt));

	return handlers;
});

export const enableHandler = command(
	z.object({ id: z.string(), enabled: z.boolean() }),
	async (data) => {
		const user = await checkAuthenticated();

		if (!user) redirect(303, '/auth/signin');

		await db
			.update(handler)
			.set({ enabled: !data.enabled })
			.where(and(eq(handler.id, data.id), eq(handler.userId, user.id)));

		getHandlers().refresh();
	}
);

export const deleteHandler = command(z.object({ id: z.string() }), async (data) => {
	const user = await checkAuthenticated();

	if (!user) redirect(303, '/auth/signin');

	await db
		.update(handler)
		.set({ deletedAt: new Date() })
		.where(and(eq(handler.id, data.id), eq(handler.userId, user.id)));
});
