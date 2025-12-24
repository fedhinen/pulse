<script>
	import { resolve } from '$app/paths';
	import { deleteHandler, enableHandler, getHandlers } from '$lib/modules/handler/handler.remote';
</script>

<div class="flex items-center justify-between mb-8">
	<div>
		<h1 class="mb-1">Handlers</h1>
		<p class="text-zinc-500 text-sm">Manage your serverless functions</p>
	</div>
	<a href={resolve('/app/handler/create')} class="bg-white text-black px-4 py-2 text-sm font-medium hover:bg-zinc-200 transition-colors no-underline">
		New Handler
	</a>
</div>

<div class="border border-zinc-800">
	<div class="grid grid-cols-12 gap-4 p-4 border-b border-zinc-800 bg-zinc-900/50 text-xs font-medium text-zinc-400 uppercase tracking-wider">
		<div class="col-span-4">Name</div>
		<div class="col-span-4">ID</div>
		<div class="col-span-2 text-center">Status</div>
		<div class="col-span-2 text-right">Actions</div>
	</div>

	{#await getHandlers()}
		<div class="p-8 text-center text-zinc-500">Loading handlers...</div>
	{:then handlers}
		{#if handlers.length === 0}
			<div class="p-8 text-center text-zinc-500">No handlers found. Create one to get started.</div>
		{:else}
			{#each handlers as { name, id, enabled } (id)}
				<div class="grid grid-cols-12 gap-4 p-4 border-b border-zinc-800 last:border-0 items-center hover:bg-zinc-900/30 transition-colors">
					<div class="col-span-4 font-medium text-white truncate">{name}</div>
					<div class="col-span-4 font-mono text-xs text-zinc-500 truncate" title={id}>{id}</div>
					<div class="col-span-2 text-center">
						<span class={`inline-flex items-center px-2 py-1 text-xs font-medium ${enabled ? 'text-green-400 bg-green-400/10' : 'text-zinc-500 bg-zinc-800'}`}>
							{enabled ? 'Active' : 'Disabled'}
						</span>
					</div>
					<div class="col-span-2 flex justify-end gap-2">
						<button
							class="p-1.5! text-xs! secondary w-auto"
							onclick={async () => {
								try {
									await enableHandler({ id, enabled }).updates(getHandlers());
								} catch (error) {
									console.log('an error', error);
								}
							}}
						>
							{enabled ? 'Disable' : 'Enable'}
						</button>
						<button
							class="p-1.5! text-xs! danger w-auto"
							onclick={async () => {
								if(!confirm('Are you sure?')) return;
								try {
									await deleteHandler({ id }).updates(getHandlers());
								} catch (error) {
									console.log('an error', error);
								}
							}}
						>
							Delete
						</button>
					</div>
				</div>
			{/each}
		{/if}
	{/await}
</div>
