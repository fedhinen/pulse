<script>
	import { resolve } from '$app/paths';
	import { deleteHandler, enableHandler, getHandlers } from '$lib/modules/handler/handler.remote';
</script>

<a href={resolve('/app/handler/create')}>New handler</a>

<h1>Handlers</h1>

<ul>
	{#each await getHandlers() as { name, id, enabled } (id)}
		<li>
			({id})
			{name}
			<button
				onclick={async () => {
					try {
						await enableHandler({ id, enabled }).updates(getHandlers());
					} catch (error) {
						console.log('an error', error);
					}
				}}>{enabled ? 'Enabled' : 'Disabled'}</button
			>
			<button
				onclick={async () => {
					try {
						await deleteHandler({ id }).updates(getHandlers());
					} catch (error) {
						console.log('an error', error);
					}
				}}
			>
				delete
			</button>
		</li>
	{/each}
</ul>
