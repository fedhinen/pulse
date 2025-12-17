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

	const originalConsole = {
		log: console.log,
		error: console.error,
		warn: console.warn,
		info: console.info
	};

	let logBuffer = '';

	const capture = (...args: unknown[]) => {
		logBuffer +=
			args.map((arg) => (typeof arg === 'string' ? arg : JSON.stringify(arg, null, 2))).join(' ') +
			'\n';
	};

	try {
		const modulePath = path.resolve(process.cwd(), './user_function');
		const userModule = await import(modulePath);

		const handler = userModule.handler || userModule.default;

		if (typeof handler !== 'function') {
			throw new Error(
				"No handler function found in user_module (looking for export 'handler' or 'default')"
			);
		}

		console.log = capture;
		console.error = capture;
		console.warn = capture;
		console.info = capture;

		const result = await handler(event);

		Object.assign(console, originalConsole);

		process.stderr.write(JSON.stringify(logBuffer));
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
