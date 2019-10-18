let elem;
let tag_list;
let parts = window.location.search.substr(1).split("&");
let $_GET = {};
for (let i = 0; i < parts.length; i++) {
	let temp = parts[i].split("=");
	$_GET[decodeURIComponent(temp[0])] = decodeURIComponent(temp[1]);
}
let filter_tags;
let passRegExp = new RegExp("^(((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})");
let resetPasswordVue;
let notificationsVue;
let registrationVue;
let loginVue;
let chatVue;

/*===================Notifications===================*/
notificationsVue = new Vue({
	el: '#notifications',
	data: {
		notifications: [],
		csrf_token: document.querySelector('meta[data-csrf-token]').getAttribute('data-csrf-token')
	},
	created() {
		elem = document.querySelector("meta[data-cur-user]");
		if (!elem || elem.getAttribute('data-cur-user') === -1)
			return;
		this.getNotifications();
		setInterval(this.getNotifications, 10000);
	},
	methods: {
		delNotification(notif_id) {
			let url = `${window.origin}/del_notification/${notif_id}`;
			axios.delete(url, {data: {csrf_token: this.csrf_token}})
				.then(() => {
					for (let i = this.notifications.length - 1; i >= 0; i--)
						if (this.notifications[i].id === notif_id)
							this.notifications.splice(i, 1);
				});
		},
		getNotifications() {
			axios.get(`${window.origin}/get_notifications`)
				.then(response => {
					this.notifications = response.data;
				})
		}
	}
});

$(document).ready(function() {
	$(document).on('click.bs.dropdown.data-api', '.notifications', function(e) {
		e.stopPropagation();
	});

	/*===================Select2===================*/
	$('.multiple-tags').select2({
		placeholder: "Interest tags",
		tags: true
	});

	filter_tags = $('.filter-tags');
	filter_tags.select2({
		placeholder: "Filter Tags"
	});

	/*===================List of Users===================*/
	function hook_like_buttons() {
		let like_user_forms = document.querySelectorAll('.like-user-ajax');
		like_user_forms.forEach(form => {
			form.onsubmit = async(e) => {
				e.preventDefault();
				let data = new FormData(form);
				form.unlike.value = data.get('unlike') == "0" ? "1" : "0";
				axios.post(`${window.origin}/ajax/like_user`, data)
					.then(response => {
						if (response.data.success) {
							form.send_button.classList.toggle('btn-success');
							form.send_button.classList.toggle('btn-danger');
							if (!response.data.unlike)
								form.send_button.innerHTML = "<i class='fas fa-thumbs-down'></i>Unlike";
							else
								form.send_button.innerHTML = "<i class='fas fa-thumbs-up'></i>Like";
							form.unlike = !form.unlike;
						} else if (response.data.error === 'KeyError') {
							$('#logIn').modal();
						}
					})
			}
		});
	}

	let user_list = document.querySelector(".users_list");
	if (user_list !== null) {
		let user_list_created = new Promise(resolve => {
			axios.get(`${window.origin}/filter_users`).then(response => {
				user_list.innerHTML = response.data;
				let user_cards = document.querySelectorAll('.user-list__card');
				for (let i = 0; i < user_cards.length; i++) {
					user_cards[i].style.animationDuration = `${.5 + (.2 * i)}s`;
				}
				resolve(true);
			});
		});
		user_list_created.then(hook_like_buttons);
	}

	/*===================Filter Users===================*/
	let loadingGif = document.querySelector('.loading');

	let filter_form = document.querySelector('.filters');
	if (filter_form) {
		filter_form.onsubmit = e => {
			user_list.innerHTML = "";
			e.preventDefault();
			let data = new FormData(filter_form);
			user_list.appendChild(loadingGif);
			let url = `${window.origin}/filter_users`;
			axios.post(url, data).then(response => {
				user_list.innerHTML = response.data;
				let user_cards = document.querySelectorAll('.user-list__card');
				for (let i = 0; i < user_cards.length; i++) {
					user_cards[i].style.animationDuration = `${.5 + (.2 * i)}s`;
				}
				hook_like_buttons();
			});
		};
	}

	elem = document.querySelector('.reset_filters');
	if (elem) elem.onclick = e => {
		e.target.form.reset();
		filter_tags.val("");
		filter_tags.trigger("change");
	};

	elem = document.querySelector('.reset_sort');
	if (elem) elem.onclick = e => {
		e.target.form.reset();
	};

	if (!tag_list && document.querySelector('.filter-tags')) {
		axios.get(`${window.origin}/ajax/get_tag_list`).then(response => {
			if (response.data.success) {
				tag_list = response.data.tags;
				filter_tags.select2({
					placeholder: "Filter Tags",
					data: tag_list
				})
			}
		})
	}

	/*===================Reset Password===================*/
	if (document.getElementById('reset')) {
		resetPasswordVue = new Vue({
			el: "#reset form",
			data: {
				action: $_GET['action'] ? $_GET['action'] : 'check',
				email: $_GET.email,
				pass: null,
				repass: null,
				error: null,
				message: null
			},
			created() {
				if (this.action === 'reset') {
					$('#reset').modal('show')
				}
			},
			methods: {
				checkForm() {
					if (!this.pass.match(passRegExp))
						this.error = "Password must be at least of length 6 and contain letters and digits";
					else if (this.repass !== this.pass)
						this.error = "Password and Re-password must be equal";
					return !this.error;
				},
				sendForm(e) {
					this.error = null;
					this.message = null;
					let data = new FormData(e.target);
					if (this.action === "reset") {
						if (!this.checkForm()) return;
						data.append("token", $_GET["token"]);
						$('#reset').modal('hide')
					}
					axios({
						method: 'post',
						url: `${window.origin}/reset`,
						data: data
					}).then(response => {
						e.target.reset();
						if (!response.data.success) {
							this.error = response.data.error;
						} else if (this.action === "check") {
							this.message = "Letter with link to re-initialize your password was sent to your E-mail!";
						} else if (this.action === "reset") {
							location.replace(location.href.split('?')[0]);
						}
					})
				}
			}
		});
	}

	/*===================Registration Form===================*/
	if (document.getElementById('signUp')) {
		registrationVue = new Vue({
			el: "#signUp form",
			data: {
				error: null,
				pass: null,
				repass: null,
				message: ""
			},
			methods: {
				checkForm() {
					if (!this.pass.match(passRegExp))
						this.error = "Password must be at least of length 6 and contain letters and digits";
					else if (this.repass !== this.pass)
						this.error = "Password and Re-password must be equal";
					return !this.error;
				},
				sendForm(e) {
					this.error = null;
					this.message = null;
					if (!this.checkForm()) return;
					axios({
						method: 'post',
						url: `${window.origin}/registration`,
						data: new FormData(e.target)
					}).then(response => {
						if (!response.data.success)
							this.error = response.data.error;
						else {
							this.message = "Registration is almost done! You should confirm your E-mail to log in.";
							e.target.reset();
						}
					})
				}
			}
		});
	}

	/*===================Login Form===================*/
	if (document.getElementById('logIn')) {
		loginVue = new Vue({
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
					}).then(response => {
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
	}

	elem = document.querySelector(".profile__avatar input");
	if (elem) elem.onchange = e => {
		e.target.parentNode.classList.add("selected");
	};

	$('.reportUser').click(function() {
		axios.post(`${window.origin}/report_user`, {
			csrf_token: $("meta[data-csrf-token]").attr('data-csrf-token'),
			unreport: $(this).hasClass('done'),
			user_id: $(this).attr('data-user-id'),
			reported_id: $(this).attr('data-reported-user-id')
		}).then(response => {
			if (response.data.success)
				$(this).toggleClass('done')
		}).catch(error => {
			console.log(error.message);
		})
	});

	/*===================Chat===================*/
	if (document.getElementById('chat')) {
		let chatPage = document.querySelector('#chat .chat');
		chatVue = new Vue({
			el: '#chat',
			data: {
				messages: [],
				sender_id: null,
				recipient_id: null,
				socket: null,
				csrf_token: null
			},
			mounted() {
				let sendMessageForm = this.$el.querySelector('form');
				this.socket = io.connect(`${window.origin}/private_chat`);
				this.sender_id = sendMessageForm.sender_id.value;
				this.recipient_id = sendMessageForm.recipient_id.value;
				this.csrf_token = sendMessageForm.csrf_token.value;
				this.showMessages();
				this.socket.on('send_message response', msg => {
					this.messages.push(msg)
				});
			},
			updated: function() {
				chatPage.scrollTop = chatPage.scrollHeight;
			},
			methods: {
				showMessages() {
					axios.post(`${window.origin}/ajax/get_messages`, {
						sender_id: this.sender_id,
						recipient_id: this.recipient_id,
						csrf_token: this.csrf_token
					}).then(response => {
						if (response.data.success) {
							this.messages = response.data.messages;
							chatPage.scrollTop = chatPage.scrollHeight;
						}
					});
				},
				sendMessage(e) {
					textInput = e.target.form.text;
					this.socket.emit('send_message event', {
						sender_id: this.sender_id,
						recipient_id: this.recipient_id,
						text: textInput.value
					});
					textInput.value = ""
				}
			}
		});
	}

	/*===================GPS===================*/
	let city;
	if ((city = document.getElementById('city')) && city.value === '') {
		let geoOptions = {timeout: 5000};
		let geoSuccess = function(position) {
			axios.get("https://maps.googleapis.com/maps/api/geocode/json", {
				params: {
					latlng: `${position.coords.latitude}, ${position.coords.longitude}`,
					key: "AIzaSyALTJ_4VStfdn39CkEBeyybal3FaxANm60",
					language: "en"
				}
			}).then(response => {
				let res = null;
				for (let i = 0; i < response.data.results.length; i++) {
					if (response.data.results[i].types.indexOf('locality') > -1) {
						res = response.data.results[i].formatted_address;
						break;
					}
				}
				if (res) {
					let splitted = res.split(', ');
					city.value = splitted[0] + ", " + splitted[1];
				}
			});
		};
		let geoError = function() {
			axios.get(location.origin + '/get_user_location_by_ip').then(response => {
				if (!response.data.success)
					console.warn(response.data.error);
				else if (response.data.address.city && response.data.address.country_name)
					city.value = `${response.data.address.city}, ${response.data.address.country_name}`;
				else
					city.value = "Kyiv, Ukraine";
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
	}, 4000);
});
