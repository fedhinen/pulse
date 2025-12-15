import { form, query } from '$app/server';
import { db } from '$lib/server/db';
import { apiKey } from '$lib/server/db/schema';
import { checkAuthenticated } from '$lib/server/db/utils';
import { eq } from 'drizzle-orm';
import { KeyCreatePreflightSchema } from './keys.schemas';
import { redirect } from '@sveltejs/kit';
import { hash } from 'argon2';

function generateRandomInteger(max: number): number {
	if (max < 0 || !Number.isInteger(max)) {
		throw new Error("Argument 'max' must be an integer greather than or equal to zero");
	}

	const bitLenght = (max - 1).toString(2).length;
	const shift = bitLenght % 8;
	const bytes = new Uint8Array(Math.ceil(bitLenght / 8));

	crypto.getRandomValues(bytes);

	if (shift !== 0) {
		bytes[0] &= (1 << shift) - 1;
	}

	let result = bytesToInteger(bytes);
	while (result > max - 1) {
		crypto.getRandomValues(bytes);
		if (shift !== 0) {
			bytes[0] &= (1 << shift) - 1;
		}

		result = bytesToInteger(bytes);
	}

	return result;
}

function bytesToInteger(bytes: Uint8Array): number {
	const binary = Array.from(bytes)
		.map((byte) => byte.toString(2).padStart(8, '0'))
		.join();

	return parseInt(binary, 2);
}

function generateRandomString(lenght: number, alphabet: string): string {
	let result = '';
	for (let i = 0; i < lenght; i++) {
		result += alphabet[generateRandomInteger(alphabet.length)];
	}

	return result;
}

export const getKeys = query(async () => {
	const user = await checkAuthenticated();

	if (!user) return redirect(303, '/auth/signin');
	return await db.select().from(apiKey).where(eq(apiKey.userId, user.id));
});

export const createKey = form(KeyCreatePreflightSchema, async (data) => {
	const user = await checkAuthenticated();

	if (!user) return redirect(303, '/auth/signin');

	const key = generateRandomString(32, '0123456789abcdefghijklmnopqrstuvwxyz');

	const secretKey = await hash(key);

	await db.insert(apiKey).values({
		id: crypto.randomUUID(),
		accessType: 'FULL',
		name: data.name,
		prefix: key.slice(0, 7),
		secretKey: secretKey,
		userId: user.id
	});

	await getKeys().refresh();

	return [{ key }, null];
});
