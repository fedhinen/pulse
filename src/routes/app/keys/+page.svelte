<script>
	import { createKey, getKeys } from '$lib/modules/keys/keys.remote';
	import { KeyCreatePreflightSchema } from '$lib/modules/keys/keys.schemas';
</script>

<h1>Api keys</h1>

{#each createKey.result as result (result)}
	{#if result?.key}
		<p>New key: {result.key}</p>
	{:else}
		<p>Hubo un error</p>
	{/if}
{/each}

<ul>
	{#each await getKeys() as { id, name, prefix } (id)}
		<li>{name} - {prefix}</li>
	{/each}
</ul>

<form {...createKey.preflight(KeyCreatePreflightSchema)}>
	<label>
		<h4>Name</h4>
		<input {...createKey.fields.name.as('text')} />
	</label>

	<button type="submit">Save</button>
</form>
