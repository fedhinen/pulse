<script lang="ts">
	import { signUp } from '$lib/modules/auth/auth.remote';
	import { SignUpSchema } from '$lib/modules/auth/auth.schemas';
</script>

<svelte:head>
	<title>Sign Up</title>
</svelte:head>

<h1>Sign Up</h1>

<form {...signUp.preflight(SignUpSchema)}>
	<label>
		<h4>Email</h4>
		<input {...signUp.fields.email.as('text')} />
	</label>
	<label>
		<h4>Password</h4>
		<input {...signUp.fields.password.as('password')} />
	</label>
	<label>
		<h4>Confirm Password</h4>
		<input {...signUp.fields.confirmPassword.as('password')} />
	</label>
	{#each signUp.fields.allIssues() as issue (issue.message)}
		<p class="issue">
			{#each issue.path as path (path)}
				{typeof path === 'number' ? `[${path}]` : `.${path}`}
			{/each}: {issue.message}
		</p>
	{/each}
	<label for="">
		<h4>Name</h4>
		<input {...signUp.fields.name.as('text')} />
	</label>

	<button type="submit">SignUp</button>
</form>
