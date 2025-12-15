<script>
	import { createHandler } from '$lib/modules/handler/handler.remote';
	import { HandlerCreatePreflightSchema } from '$lib/modules/handler/handler.schemas';
</script>

<h4>New Handler</h4>

<form {...createHandler.preflight(HandlerCreatePreflightSchema)} enctype="multipart/form-data">
	<label>
		<h4>Nombre</h4>
		<input {...createHandler.fields.name.as('text')} />
	</label>
	<label>
		<h4>Asincrono</h4>
		<input {...createHandler.fields.async.as('checkbox')} />
	</label>
	<label>
		<h4>Codigo</h4>
		<input {...createHandler.fields.file.as('file')} />
	</label>

	{#each createHandler.fields.allIssues() as issue (issue.message)}
		<p class="issue">
			{#each issue.path as path (path)}
				{typeof path === 'number' ? `[${path}]` : `.${path}`}
			{/each}: {issue.message}
		</p>
	{/each}

	<button type="submit">Create Handler</button>
</form>
