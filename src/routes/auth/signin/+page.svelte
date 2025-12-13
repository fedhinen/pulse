<script lang="ts">
	import { resolve } from '$app/paths';
	import { signIn } from '$lib/modules/auth/auth.remote';
	import { SignInSchema } from '$lib/modules/auth/auth.schemas';
</script>

<svelte:head>
	<title>Sign In</title>
</svelte:head>

<h1>Sign In</h1>

<form {...signIn.preflight(SignInSchema)}>
	<label>
		<h4>Email</h4>
		<input {...signIn.fields.email.as('text')} />
	</label>
	<label>
		<h4>Password</h4>
		<input {...signIn.fields.password.as('password')} />
	</label>
	<label>
		<h4>Remember Me</h4>
		<input {...signIn.fields.rememberMe.as('checkbox')} />
	</label>
	{#each signIn.fields.allIssues() as issue (issue.message)}
		<p class="issue">
			{#each issue.path as path (path)}
				{typeof path === 'number' ? `[${path}]` : `.${path}`}
			{/each}: {issue.message}
		</p>
	{/each}

	<a href={resolve('/auth/signup/')}>Sign Up</a>

	<button type="submit">Sign In</button>
</form>
