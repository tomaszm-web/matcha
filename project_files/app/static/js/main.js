let elem;

if (document.getElementById('notifications')) {
	$(document).on('click.bs.dropdown.data-api', '.notifications', function(e) {
	   e.stopPropagation();
	});
	notifications = new Vue({
		el: '#notifications',
		data: {
			notifications: [],
			csrf_token: document.querySelector('meta[data-csrf-token]').getAttribute('data-csrf-token')
		},
		created() {
			this.getNotifications();
			setInterval(this.getNotifications, 10000);
		},
		methods: {
			delNotification(notif_id) {
				let url = `${window.origin}/del_notification/${notif_id}`;
				axios.delete(url, { data: {csrf_token: this.csrf_token} })
					 .then(() => {
						 for (let i = this.notifications.length - 1; i >= 0; i--)
							 if (this.notifications[i].id === notif_id)
							 	this.notifications.splice(i, 1);
					});
			},
			getNotifications() {
				axios.get(`${window.origin}/get_notifications`)
					.then((response) => {
						this.notifications = response.data;
					})
			}
		}
	});
}

let user_list = document.querySelector(".users_list");
if (user_list !== null) {
	let user_list_created = new Promise(resolve => {
		axios.get(`${window.origin}/filter_users`).then(response => {
			user_list.innerHTML = response.data;
			resolve(true);
		});
	});
	user_list_created.then(() => {
		let like_buttons = document.querySelectorAll('.like-user');
		like_buttons.forEach(button => {
			button.onclick = async() => {
				let data = {
					unlike: button.classList.contains('done'),
					liked_user: button.getAttribute('data-liked-user-id'),
					csrf_token: button.getAttribute('data-csrf')
				};
				axios.post(`${window.origin}/ajax/like_user`, data).then(response => {
						if (response.data.success) {
							button.classList.toggle('done');
						} else if (response.data.error === 'KeyError') {
							$('#logIn').modal();
						}
					 })
			}
		});
	});
}

$(document).ready(function() {
	let parts = window.location.search.substr(1).split("&");
	let $_GET = {};
	for (let i = 0; i < parts.length; i++) {
		let temp = parts[i].split("=");
		$_GET[decodeURIComponent(temp[0])] = decodeURIComponent(temp[1]);
	}

	let loadingGif = document.querySelector('.loading');
	$('.filters').submit(function(e) {
		e.preventDefault();
		let data = new FormData(e.target);
		user_list.innerHTML = "";
		user_list.appendChild(loadingGif);
		axios.post(`${window.origin}/filter_users`, data).then(response => {
			user_list.innerHTML = response.data;
		});
	});

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
						if (!response.data.success)
							this.errors.push(response.data.cause);
						else {
							this.message = "Registration is almost done! You should confirm your E-mail to log in."
							e.target.reset();
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
				axios({
					method: 'post',
					url: `${window.origin}/login`,
					data: new FormData(e.target)
				}).then((response) => {
					if (response.data.success) {
						this.error = null;
						location.reload()
					} else {
						this.error = response.data.error
					}
				}).catch((error) => {
					this.error = error
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
			checkForm() {
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

	elem = document.querySelector(".profile__avatar input");
	if (elem) elem.onchange = (e) => {
		e.target.parentNode.classList.add("selected");
	};

	$('.multiple-tags').select2({
		placeholder: "Interest tags",
		tags: true
	});

	$('.blockUser').click(function() {
		axios.get(location.origin + '/block_user', {
			params: {
				unblock: $(this).hasClass('done'),
				user_id: $(this).attr('data-user-id'),
				blocked_id: $(this).attr('data-blocked-user-id')
			}
		}).then((response) => {
			if (response.data.success)
				$(this).toggleClass('done')
		})
	});

	$('.reportUser').click(function() {
		axios.get(location.origin + '/report_user', {
			params: {
				unreport: $(this).hasClass('done'),
				user_id: $(this).attr('data-user-id'),
				reported_id: $(this).attr('data-reported-user-id')
			}
		}).then((response) => {
			if (response.data.success)
				$(this).toggleClass('done')
		})
	});

	/*--------Chat--------*/
	if (document.getElementById('chat')) {
		const chat = new Vue({
			el: '#chat',
			data: {
				messages: [],
				sender_id: null,
				recipient_id: null,
				socket: null
			},
			created() {
				this.socket = io.connect(location.origin + '/private_chat');
				this.recipient_id = $_GET['recipient_id'];
				this.sender_id = $(".sendMessageForm input[name='sender_id']").val();
				this.showMessages();
				this.socket.on('private_chat response', (msg) => {
					this.messages.push(msg)
				});
			},
			updated: function() {
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
						if (response.data.success) {
							this.messages = response.data.messages;
						}
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

	/*--------Notifications--------*/



	/*--------GPS--------*/
	let city;
	if ((city = document.getElementById('city')) && elem.value !== '') {
		let geoOptions = {timeout: 5000};
		let geoSuccess = function(position) {
			axios.get("https://maps.googleapis.com/maps/api/geocode/json", {
				params: {
					latlng: position.coords.latitude + ', ' + position.coords.longitude,
					key: "AIzaSyAjzkW8XWRsKcQhs7hcY-Rc7wPSSSIQVQM",
					language: "en"
				}
			}).then((response) => {
				let res = null;
				for (let i = 0; i < response.data.results.length; i++) {
					if (response.data.results[i].types.indexOf('locality') > -1) {
						res = response.data.results[i].formatted_address;
						break;
					}
				}
				if (res) {
					var splitted = res.split(', ');
					city.value = splitted[0] + ", " + splitted[1];
				}
			});
		};
		let geoError = function() {
			axios.get(location.origin + '/get_user_location_by_ip').then((response) => {
				if (!response.data.success) {
					// console.warn(response.data.cause);
				} else if (response.data.address.city && response.data.address.country_name) {
					city.value = response.data.address.city + ", " + response.data.address.country_name;
				} else {
					city.value = "Kyiv, Ukraine";
				}
			});
		};
		navigator.geolocation.getCurrentPosition(geoSuccess, geoError, geoOptions);
	}

	const autocomplete_options = {
		types: ['(cities)'],
		language: 'en'
	};
	if ((elem = document.getElementById('city')))
		new google.maps.places.Autocomplete(elem, autocomplete_options);
	if ((elem = document.getElementById('select-city')))
		new google.maps.places.Autocomplete(elem, autocomplete_options);

	setTimeout(function() {
		$('.flashes').css('opacity', 0);
	}, 7000);
});
