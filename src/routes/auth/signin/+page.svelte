<script lang="ts">
	import { resolve } from '$app/paths';
	import { signIn } from '$lib/modules/auth/auth.remote';
	import { SignInSchema } from '$lib/modules/auth/auth.schemas';
</script>

<svelte:head>
	<title>Sign In</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center px-4">
	<div class="w-full max-w-sm">
		<div class="mb-8 text-center">
			<h1 class="mb-2">Sign In</h1>
			<p class="text-zinc-500 text-sm">Enter your credentials to access your account</p>
		</div>

		<form {...signIn.preflight(SignInSchema)} class="space-y-4">
			<label>
				<h4>Email</h4>
				<input {...signIn.fields.email.as('text')} type="email" placeholder="name@example.com" />
			</label>
			<label>
				<h4>Password</h4>
				<input {...signIn.fields.password.as('password')} type="password" placeholder="••••••••" />
			</label>
			<div class="flex items-center justify-between mb-4">
				<label class="flex items-center gap-2 mb-0 cursor-pointer">
					<input {...signIn.fields.rememberMe.as('checkbox')} class="w-4 h-4" />
					<span class="text-sm text-zinc-400">Remember me</span>
				</label>
			</div>

			{#each signIn.fields.allIssues() as issue (issue.message)}
				<p class="issue">
					{#each issue.path as path (path)}
						{typeof path === 'number' ? `[${path}]` : `.${path}`}
					{/each}: {issue.message}
				</p>
			{/each}

			<button type="submit" class="w-full">Sign In</button>

			<p class="text-center text-sm text-zinc-500 mt-6">
				Don't have an account? 
				<a href={resolve('/auth/signup/')} class="text-white hover:underline">Sign Up</a>
			</p>
		</form>
	</div>
</div>
