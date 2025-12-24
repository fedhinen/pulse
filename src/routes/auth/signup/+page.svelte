<script lang="ts">
	import { resolve } from '$app/paths';
	import { signUp } from '$lib/modules/auth/auth.remote';
	import { SignUpSchema } from '$lib/modules/auth/auth.schemas';
</script>

<svelte:head>
	<title>Sign Up</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center px-4">
	<div class="w-full max-w-sm">
		<div class="mb-8 text-center">
			<h1 class="mb-2">Sign Up</h1>
			<p class="text-zinc-500 text-sm">Create a new account to get started</p>
		</div>

		<form {...signUp.preflight(SignUpSchema)} class="space-y-4">
			<label>
				<h4>Name</h4>
				<input {...signUp.fields.name.as('text')} type="text" placeholder="John Doe" />
			</label>
			<label>
				<h4>Email</h4>
				<input {...signUp.fields.email.as('text')} type="email" placeholder="name@example.com" />
			</label>
			<label>
				<h4>Password</h4>
				<input {...signUp.fields.password.as('password')} type="password" placeholder="••••••••" />
			</label>
			<label>
				<h4>Confirm Password</h4>
				<input {...signUp.fields.confirmPassword.as('password')} type="password" placeholder="••••••••" />
			</label>

			{#each signUp.fields.allIssues() as issue (issue.message)}
				<p class="issue">
					{#each issue.path as path (path)}
						{typeof path === 'number' ? `[${path}]` : `.${path}`}
					{/each}: {issue.message}
				</p>
			{/each}

			<button type="submit" class="w-full">Sign Up</button>

			<p class="text-center text-sm text-zinc-500 mt-6">
				Already have an account? 
				<a href={resolve('/auth/signin/')} class="text-white hover:underline">Sign In</a>
			</p>
		</form>
	</div>
</div>
