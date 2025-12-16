import { db } from '$lib/server/db/index.js';
import { apiKey, handler, keyPermissions } from '$lib/server/db/schema.js';
import { error, json } from '@sveltejs/kit';
import { verify } from 'argon2';
import { and, eq } from 'drizzle-orm';

export async function GET({ params, request }) {
	const handlerId = params.uid;
	const xPulseKey = request.headers.get('X-Pulse-Key');

	if (!xPulseKey) return error(400, 'X-Pulse-Key is required');

	const [data] = await db.select().from(handler).where(eq(handler.id, handlerId)).limit(1);

	if (!data) return error(400, 'Handler not found');

	if (!data.enabled) return error(400, 'Handler not enabled');

	const scopedPermissions = await db
		.select()
		.from(keyPermissions)
		.where(and(eq(keyPermissions.handlerId, handlerId), eq(keyPermissions.userId, data.userId)));

	if (scopedPermissions.length) {
		// Para permisos scoped
	}

	const apiKeys = await db
		.select()
		.from(apiKey)
		.where(and(eq(apiKey.userId, data.userId), eq(apiKey.accessType, 'FULL')));

	let hasPermissions = false;
	for (const keys of apiKeys) {
		if (hasPermissions) continue;
		const isVerified = await verify(keys.secretKey, xPulseKey);

		hasPermissions = isVerified;
	}

	if (!hasPermissions) return error(400, 'Invalid Api key');

	const { id, fileName, filePath, name, runtime, async } = data;

	return json(
		{ id, fileName, filePath, name, runtime, isAsync: async },
		{
			status: 200
		}
	);
}
