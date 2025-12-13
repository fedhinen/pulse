import z from 'zod';

export const SignUpSchema = z
	.object({
		email: z.email(),
		password: z.string().check(z.minLength(8), z.maxLength(100), z.trim()),
		name: z.string().check(z.minLength(1), z.maxLength(100), z.trim()),
		confirmPassword: z.string().check(z.minLength(8), z.maxLength(100), z.trim())
	})
	.refine((data) => data.password === data.confirmPassword, {
		message: 'Passwords do not match'
	});

export const SignInSchema = z.object({
	email: z.email(),
	password: z.string().check(z.minLength(8), z.maxLength(100), z.trim()),
	rememberMe: z.boolean().optional()
});
