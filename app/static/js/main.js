$(document).ready(function () {
	let parts = window.location.search.substr(1).split("&");
	let $_GET = {};
	for (let i = 0; i < parts.length; i++) {
		let temp = parts[i].split("=");
		$_GET[decodeURIComponent(temp[0])] = decodeURIComponent(temp[1]);
	}
	let socket = io.connect(location.origin);

	if ($('.users_list')) {
		axios.get(location.origin + '/filter_users').then((response) => {
			$('.users_list').html(response.data);
		});
	}

	if ($('.filters')) {
		$('.filters').submit(function (e) {
			e.preventDefault();
			let data = new FormData(e.target)
			axios.post(location.origin + '/filter_users', data).then((response) => {
				$('.users_list').html(response.data);
			});
		})
	}

	/*--------Forms--------*/
	let passRegExp = new RegExp("^(((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})");

	let registration = new Vue({
		el: "#signUp form",
		data: {
			errors: [],
			pass: null,
			repass: null,
			message: ""
		},
		methods: {
			checkForm() {
				this.errors = [];
				if (!this.pass.match(passRegExp))
					this.errors.push("Password must be at least of length 6 and contain letters and digits");
				else if (this.repass !== this.pass)
					this.errors.push("Password and Re-password must be equal");
				return this.errors.length === 0;
			},
			sendForm(e) {
				if (this.checkForm()) {
					axios({
						method: 'post',
						url: '/registration',
						data: new FormData(e.target)
					}).then((response) => {
						this.errors.push.apply(this.errors, response.data);
						if (!this.errors.length) {
							e.target.reset();
							this.message = "Registration is almost done! You should confirm your E-mail to log in."
						}
					}).catch(() => {
						this.errors.push("Something went wrong! Try again")
					});
				}
			}
		}
	});

	let login = new Vue({
		el: "#logIn form",
		data: {
			error: null,
			message: ""
		},
		methods: {
			sendForm(e) {
				this.errors = [];
				axios({
					method: 'post',
					url: '/login',
					data: new FormData(e.target)
				}).then((response) => {
					if (response.data.success) {
						this.error = null;
						location.reload()
					} else {
						this.error = response.data.cause
					}
				}).catch(() => {
					this.errors.push("Something went wrong! Try again")
				});
			}
		}
	});

	let reset = new Vue({
		el: "#reset form",
		data: {
			action: "action" in $_GET && "email" in $_GET && "token" in $_GET ? $_GET["action"] : "check",
			email: null,
			pass: null,
			repass: null,
			errors: [],
			message: ""
		},
		created() {
			if ("action" in $_GET && $_GET["action"] == "reset") {
				$("#reset").modal("show");
				this.action = $_GET.action;
				this.email = $_GET["email"];
			}
		},
		methods: {
			checkForm(action) {
				this.errors = [];
				if (!this.pass || !this.repass)
					this.errors.push("Empty password");
				else if (!this.pass.match(passRegExp))
					this.errors.push("Password must be at least of length 6 and contain letters and digits");
				else if (this.repass !== this.pass)
					this.errors.push("Password and Re-password must be equal");
				return this.errors.length === 0;
			},
			sendForm(e) {
				this.errors = [];
				this.message = "";
				let data = new FormData(e.target);
				if (this.action === "reset") {
					if (!this.checkForm()) return;
					data.append("token", $_GET["token"]);
				}
				axios({
					method: 'post',
					url: '/reset',
					data: data
				}).then((response) => {
					e.target.reset();
					if (!response.data.success) {
						this.errors.push(response.data.error);
					} else {
						if (this.action === "check")
							this.message = "Letter with link to re-initialize your password was sent to your E-mail!"
						else if (this.action === "reset")
							location.replace(location.href.split('?')[0]);
					}
				}).catch(() => {
					this.errors.push("Something went wrong! Try again")
				});
			}
		}
	});

	let elem = document.querySelector(".profile__avatar input");
	if (elem) elem.onchange = (e) => {
		e.target.parentNode.classList.add("selected");
	};

	$('.multiple-tags').select2({
		placeholder: "Interest tags",
		tags: true
	});

	$('.city-select').select2({
		placeholder: "Choose city"
	});

	$('.likeUser').click(function () {
		axios.get(location.origin + '/like_user', {
			params: {
				unlike: $(this).hasClass('done'),
				like_owner: $(this).attr('data-user-id'),
				liked_user: $(this).attr('data-liked-user-id')
			}
		}).then((response) => {
			if (response.data.success)
				$(this).toggleClass('done')
		}).catch(() => {
			console.log("Something went wrong! Try again")
		});
	});

	$('.blockUser').click(function () {
		axios.get(location.origin + '/block_user', {
			params: {
				unblock: $(this).hasClass('done'),
				user_id: $(this).attr('data-user-id'),
				blocked_id: $(this).attr('data-blocked-user-id')
			}
		}).then((response) => {
			if (response.data.success)
				$(this).toggleClass('done')
		}).catch(() => {
			console.log("Something went wrong! Try again")
		});
	});

	/*--------Chat--------*/
	if (document.getElementById('chat')) {
		const chat = new Vue({
			el: '#chat',
			data: {
				messages: {},
				sender_id: null,
				recipient_id: null,
				socket: null
			},
			created() {
				this.socket = io.connect(location.origin + '/private_chat');
				this.recipient_id = $_GET['recipient_id'];
				this.sender_id = $(".sendMessageForm input[name='sender_id']").val();
				this.messages = this.showMessages();
				this.socket.on('connect', function () {
					console.log('connected to private chat')
				});
				this.socket.on('private_chat response', (msg) => {
					this.messages.push(msg)
				});
			},
			updated: function () {
				const el = document.querySelector('#chat .chat');
				el.scrollTop = el.scrollHeight;
			},
			methods: {
				showMessages() {
					axios.get(location.origin + '/get_messages', {
						params: {
							sender_id: this.sender_id,
							recipient_id: this.recipient_id,
						}
					}).then((response) => {
						if (response.data.success)
							this.messages = response.data.messages;
					});
				},
				sendMessage(e) {
					this.socket.emit('private_chat event', {
						sender_id: this.sender_id,
						recipient_id: this.recipient_id,
						body: e.target.text.value
					});
					e.target.text.value = ""
				}
			}
		});
	}

	/*--------GPS--------*/
	let geoOptions = {
		timeout: 10 * 1000
	};
	let startPos;
	let geoSuccess = function (position) {
		startPos = position
	};
	let geoError = function () {
		console.log('Error occurred. Error code: ' + error.code);
		// error.code can be:
		//   0: unknown error
		//   1: permission denied
		//   2: position unavailable (error response from location provider)
		//   3: timed out
	};
	navigator.geolocation.getCurrentPosition(geoSuccess, geoError, geoOptions);

	axios.get("https://maps.googleapis.com/maps/api/geocode/json?latlng=50.4705531,30.464246900000003&key=AIzaSyAjzkW8XWRsKcQhs7hcY-Rc7wPSSSIQVQM").then((response) => {
		console.log(response.data);
	});
});
