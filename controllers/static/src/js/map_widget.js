/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { useExternalListener } from "@odoo/owl";

const { Component, onMounted, onWillUpdateProps, useRef } = owl;

export class MapPickerWidget extends CharField {
    static template = "gym_management.MapPickerWidget";

    setup() {
        super.setup();
        this.mapRef = useRef("map");
        this.map = null;
        this.marker = null;

        // Default coordinates (Jakarta, Indonesia) if value is empty
        this.DEFAULT_LAT = -6.2088;
        this.DEFAULT_LNG = 106.8456;

        onMounted(() => {
            this.loadMap();
        });

        onWillUpdateProps((nextProps) => {
            this.updateMarker(nextProps.value);
        });
    }

    getCoords(value) {
        if (value && value.includes(',')) {
            const parts = value.split(',');
            const lat = parseFloat(parts[0]);
            const lng = parseFloat(parts[1]);
            if (!isNaN(lat) && !isNaN(lng)) {
                return [lat, lng];
            }
        }
        return [this.DEFAULT_LAT, this.DEFAULT_LNG];
    }

    loadMap() {
        const coords = this.getCoords(this.props.value);

        // Load Leaflet CSS if not already loaded
        if (!document.querySelector('link[href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
            document.head.appendChild(link);
        }
        
        // Load Leaflet JS
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.onload = () => {
            this.map = L.map(this.mapRef.el).setView(coords, 13);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);

            this.marker = L.marker(coords).addTo(this.map);

            this.map.on('click', (e) => {
                const lat = e.latlng.lat;
                const lng = e.latlng.lng;
                const newValue = `${lat},${lng}`;
                
                // Update the field value in Odoo
                this.props.update(newValue);

                // Move the marker
                this.marker.setLatLng(e.latlng);
            });
        };
        document.head.appendChild(script);
    }

    updateMarker(value) {
        if (this.map && this.marker) {
            const coords = this.getCoords(value);
            const latLng = L.latLng(coords[0], coords[1]);
            this.marker.setLatLng(latLng);
            this.map.panTo(latLng);
        }
    }
}

registry.category("fields").add("map_picker", MapPickerWidget);