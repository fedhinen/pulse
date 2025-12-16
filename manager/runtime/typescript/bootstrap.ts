import path from 'path';

async function run() {
	const inputData = await Bun.stdin.text();

	let event = {};
	try {
		event = inputData ? JSON.parse(inputData) : {};
	} catch (e) {
		console.log('Error parsing input JSON, defaulting to empty event object.', e);
		event = {};
	}

	try {
		const modulePath = path.resolve(process.cwd(), './user_function');
		const userModule = await import(modulePath);

		const handler = userModule.handler || userModule.default;

		if (typeof handler !== 'function') {
			throw new Error(
				"No handler function found in user_module (looking for export 'handler' or 'default')"
			);
		}

		const result = await handler(event);

		process.stdout.write(JSON.stringify({ status: 'success', output: result }));
	} catch (error) {
		if (error instanceof Error) {
			process.stdout.write(
				JSON.stringify({
					status: 'error',
					error: error.message || String(error),
					trace: error.stack || null // Incluimos el stacktrace
				})
			);
		}
	}
}

run();
