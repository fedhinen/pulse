import { form } from '$app/server';
import { auth } from '$lib/auth';
import { redirect } from '@sveltejs/kit';
import { SignInSchema, SignUpSchema } from './auth.schemas';

export const signUp = form(SignUpSchema, async (data) => {
	console.log('Signing up user with data:', data);
	const user = await auth.api.signUpEmail({
		body: {
			email: data.email,
			password: data.password,
			name: data.name
		}
	});

	console.log('User signed up successfully:', user);

	redirect(303, '/auth/signin');
});

export const signIn = form(SignInSchema, async (data) => {
	console.log('Signing in user with data:', data);
	await auth.api.signInEmail({
		body: {
			email: data.email,
			password: data.password,
			rememberMe: data.rememberMe || false
		}
	});

	redirect(303, '/app');
});
