/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { onMounted, onWillUnmount, useRef } from "@odoo/owl";

export class LeafletMapWidget extends CharField {
    setup() {
        super.setup();
        this.mapContainer = useRef("mapContainer");
        this.map = null;
        this.marker = null;

        onMounted(() => {
            // Pastikan elemen container ada sebelum me-render peta
            if (this.mapContainer.el) {
                this.renderMap();
            }
        });

        onWillUnmount(() => {
            if (this.map) {
                this.map.remove();
            }
        });
    }

    renderMap() {
        // Default coordinates (e.g., Jakarta, Indonesia) if no value
        let lat = -6.2088;
        let lng = 106.8456;
        let zoom = 13;

        // PERBAIKAN: Tambahkan pemeriksaan untuk props.record.data
        const value = this.props.record.data ? this.props.record.data[this.props.name] : null;
        if (value) {
            const parts = value.split(',');
            if (parts.length === 2) {
                const parsedLat = parseFloat(parts[0]);
                const parsedLng = parseFloat(parts[1]);
                // Pastikan hasil parse adalah angka
                if (!isNaN(parsedLat) && !isNaN(parsedLng)) {
                    lat = parsedLat;
                    lng = parsedLng;
                }
            }
        }

        // Initialize map
        this.map = L.map(this.mapContainer.el).setView([lat, lng], zoom);

        // Add tile layer from OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(this.map);

        // Add marker
        this.marker = L.marker([lat, lng], { draggable: true }).addTo(this.map);

        // Event listener for map click
        this.map.on('click', (e) => {
            this.updateCoordinates(e.latlng);
        });

        // Event listener for marker drag
        this.marker.on('dragend', (e) => {
            this.updateCoordinates(e.target.getLatLng());
        });
    }

    updateCoordinates(latlng) {
        const { lat, lng } = latlng;
        const newValue = `${lat.toFixed(7)},${lng.toFixed(7)}`;

        // Update marker position
        this.marker.setLatLng(latlng);
        this.map.panTo(latlng);

        // Update Odoo field value
        this.props.record.update({ [this.props.name]: newValue });
    }
}

// Definisikan template untuk widget
LeafletMapWidget.template = "gym_management.LeafletMapWidget";

// Daftarkan widget baru ke dalam registry Odoo
registry.category("fields").add("leaflet_map_widget", LeafletMapWidget);