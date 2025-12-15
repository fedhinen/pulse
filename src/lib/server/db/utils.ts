// src/lib/server/utils.ts (or wherever you define remote functions)
import { getRequestEvent } from '$app/server';
import { auth } from '$lib/auth'; // Your better-auth server instance

export async function checkAuthenticated() {
	const event = getRequestEvent();
	if (!event) {
		throw new Error('Cannot access request event outside of server context');
	}

	const session = await auth.api.getSession({
		headers: event.request.headers
	});

	if (!session?.user) {
		throw new Error('Unauthorized: User not authenticated');
	}

	return session.user;
}
