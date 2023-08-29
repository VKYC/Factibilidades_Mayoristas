odoo.define('widget_map.FieldMap', function (require) {
	'use strict';

	var registry = require('web.field_registry');
	var AbstractField = require('web.AbstractField');

	var FieldMap = AbstractField.extend({
		template: 'FieldMap',
		supportedFieldTypes: ['char'],
		// isQuickEditable: false,

		start: function () {
			var self = this;
			this.autocomplete = this.$el[0];
			this.information = new google.maps.InfoWindow();

			this.map = new google.maps.Map(this.$el[2], {
				center: { lat: 0, lng: 0 },
				zoom: 0,
				disableDefaultUI: true,
			});
			this.marker = new google.maps.Marker({
				position: { lat: 0, lng: 0 },
			});

			this.search = new google.maps.places.Autocomplete(this.autocomplete);
			this.search.bindTo('bounds', this.map);
			// this.search.setFields(['formatted_address', 'geometry', 'name']);

			this.call('bus_service', 'onNotification', this, this._onLongpollingNotifications);

			this.search.addListener('place_changed', function () {
				if (self.mode === 'edit') {
					self.information.close();
					self.marker.setVisible(false);
					var place = self.search.getPlace();
					if (!place.geometry.viewport) {
						window.alert('Error');
						return;
					}

					if (place.geometry.viewport) {
						self.map.fitBounds(place.geometry.viewport);
						self.marker.setPosition(place.geometry.location);
					} else {
						self.map.setCenter(place.geometry.location);
						self.setZoom(18);
					}
					self.marker.setPosition(place.geometry.location);
					self.marker.setVisible(true);
					var value = JSON.stringify({
						position: place.geometry.location,
						zoom: self.map.getZoom(),
						autocomplete:
							self.getFormattedPrediction()
					});

					self._setValue(value);
					var address = '';
					if (place.address_components) {
						address = [
							(place.address_components[0] && place.address_components[0].short_name) || '',
							(place.address_components[1] && place.address_components[1].short_name) || '',
							(place.address_components[2] && place.address_components[2].short_name) || '',
						];
					} else {
						address = self.autocomplete.value;
					}
					if (address !== '') {
						self.information.setContent('<div> <strong>' + place.name + '</strong><br>' + address + '</div>');
						self.information.open(self.map, self.marker);
					}
				}
			});

			this.map.addListener('click', function (e) {
				if (self.mode === 'edit') {
					if (!self.get('effective_readonly') && self.marker.getMap() == null) {
						self.marker.setPosition(e.latLng);
						self.marker.setMap(self.map);
						self._setValue(
							JSON.stringify({
								position: self.marker.getPosition(),
								zoom: self.map.getZoom(),
								autocomplete:
									self.getFormattedPrediction()
							})
						);
					}
				}
			});
			// this.map.addListener('zoom_changed', function () {
			// 	if (self.mode === 'edit') {
			// 		if (!self.get('effective_readonly') && self.marker.getMap()) {
			// 			self._setValue(
			// 				JSON.stringify({
			// 					position: self.marker.getPosition(),
			// 					zoom: self.map.getZoom(),
			// 					autocomplete:
			// 						self.getFormattedPrediction()
			// 				})
			// 			);
			// 		}
			// 	}
			// });

			this.marker.addListener('click', function () {
				if (self.mode === 'edit') {
					if (!self.get('effective_readonly')) {
						self.marker.setMap(null);
						self._setValue(false);
					}
				}
			});
			this.marker.addListener('dragend', function () {
				if (self.mode === 'edit') {
					self.information.open(self.map, self.marker);
					self._setValue(
						JSON.stringify({
							position: self.marker.getPosition(),
							zoom: self.map.getZoom(),
							autocomplete:
								self.getFormattedPrediction(),
						})
					);
					// self.marker.setPosition(place.geometry.location);
					self.marker.setVisible(true);
				}
			});
			this.getParent()
				.$('a[data-toggle="tab"]')
				.on('shown.bs.tab', function () {
					if (self.mode === 'edit') {
						self.trigger('resize');
					}
				});
			this.getParent().on('attached', this.getParent(), function () {
				if (self.mode === 'edit') {
					self.trigger('resize');
				}
			});

			this.on('change:effective_readonly', this, function () {
				if (self.mode === 'edit') {
					this.update_mode;
				}
			});
			this.on('resize', this, function () {
				if (self.mode === 'edit') {
					this._toggle_label;
				}
			});
			this.update_mode();
			this._super();
		},

		getFormattedPrediction: function () {
			this.information.close();
			// this.marker.setVisible(false);
			var place = this.search.gm_accessors_.place
			for (let key in place) {
				if (place[key].formattedPrediction !== undefined) {
					return place[key].formattedPrediction
				}
			}
			return this.autocomplete.value
		},

		async _onLongpollingNotifications(notifications) {
			for (const { type } of notifications) {
				if (type === 'onchange_address') {
					// console.log('onchange_geolocation');
					if (this.value) {
						var inputText = JSON.parse(this.value).autocomplete;
						var request = {
							// location: pyrmont,
							// radius: '500',
							query: inputText,
						};
						$(this.autocomplete).val(inputText);
						var service = new google.maps.places.PlacesService(this.map);
						var place;
						var self = this;

						function callback(results, status) {
							if (status == google.maps.places.PlacesServiceStatus.OK) {
								if (results.length > 0) {
									place = results[0];
									self.information.close();
									self.marker.setVisible(false);

									if (!place.geometry.viewport) {
										window.alert('Error');
										return;
									}

									if (place.geometry.viewport) {
										self.map.fitBounds(place.geometry.viewport);
										self.marker.setPosition(place.geometry.location);
									} else {
										self.map.setCenter(place.geometry.location);
										self.setZoom(18);
									}
									self.marker.setPosition(place.geometry.location);
									self.marker.setVisible(true);
									var value = JSON.stringify({
										position: place.geometry.location,
										zoom: self.map.getZoom(),
										autocomplete:
											// self.getFormattedPrediction()
											inputText
									});

									self._setValue(value);
									var address = '';
									if (place.address_components) {
										address = [
											(place.address_components[0] && place.address_components[0].short_name) || '',
											(place.address_components[1] && place.address_components[1].short_name) || '',
											(place.address_components[2] && place.address_components[2].short_name) || '',
										];
									} else {
										address = self.autocomplete.value;
									}
									if (address !== '') {
										self.information.setContent('<div> <strong>' + place.name + '</strong><br>' + address + '</div>');
										self.information.open(self.map, self.marker);
									}
								}
							}
						}

						service.textSearch(request, callback);
					}
				}
				else {
					if (type === 'onchange_longitude_latitude' && this.value) {
						this.marker.setPosition(JSON.parse(this.value).position);
						this.map.setCenter(JSON.parse(this.value).position);
						this.map.setZoom(JSON.parse(this.value).zoom);
						$(this.autocomplete).val(this.getFormattedPrediction());
						this.marker.setMap(this.map);

						this.marker.setVisible(true);

						// var value = JSON.stringify({
						// 	position: this.marker.getPosition(),
						// 	zoom: this.map.getZoom(),
						// 	autocomplete:
						// 		this.getFormattedPrediction()
						// });

						// this._setValue(value);

					}
				}

			}
		},

		render_value: function () {
			if (this.value) {
				this.marker.setPosition(JSON.parse(this.value).position);
				this.map.setCenter(JSON.parse(this.value).position);
				this.map.setZoom(JSON.parse(this.value).zoom);
				$(this.autocomplete).val(JSON.parse(this.value).autocomplete);
				this.marker.setMap(this.map);
			} else {
				this.marker.setPosition({ lat: 0, lng: 0 });
				this.map.setCenter({ lat: 0, lng: 0 });
				this.map.setZoom(2);
				this.marker.setMap(null);
			}
		},
		update_mode: function () {
			if (this.get('effective_readonly')) {
				this.map.setOptions({
					disableDoubleClickZoom: true,
					draggable: false,
					scrollwheel: false,
				});
				this.marker.setOptions({
					draggable: false,
					cursor: 'default',
				});
			} else {
				this.map.setOptions({
					disableDoubleClickZoom: false,
					draggable: true,
					scrollwheel: true,
				});
				this.marker.setOptions({
					draggable: true,
					cursor: 'pointer',
				});
			}
			this.render_value();
		},
		_toggle_label: function () {
			this._super();
			google.maps.event.trigger(this.map, 'resize');
			if (!this.no_rerender) {
				this.render_value();
			}
		},
	});

	registry.add('map', FieldMap);

	return FieldMap;

	// core.form_widget_registry.add('map', FieldMap);

	// return {
	// 	FieldMap: FieldMap,
	// };
});
