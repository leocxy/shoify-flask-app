<template>
    <div class="container install-block">
        <div class="input-group">
            <input type="text" v-model="store_url" name="store_url" class="input-text-field"
                   placeholder="your-store.myshopify.com" autocomplete="off"/>
            <button class="btn" :disabled="error" @click="install">Install</button>
        </div>
        <span class="error-tip" v-show="error">Please enter a valid store url</span>
    </div>
</template>

<script>
export default {
    name: "Installer",
    data: () => ({
        store_url: null,
        error: false,
    }),
    watch: {
        store_url: function (e) {
            this.error = (e.match(/(.*)\.myshopify\.com$/g) == null)
        }
    },
    methods: {
        install: function () {
            this.error = (this.store_url.match(/(.*)\.myshopify\.com$/g) == null);
            if (!this.error) window.location.href = `${window.location.origin}/install?shop=${this.store_url}`
        }
    }
}
</script>

<style lang="scss" scoped>
$border-color: #ccc;
$laybuy-purple: #786dff;
$error-color: #DA5961;
.container.install-block {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;

    .error-tip {
        width: 100%;
        max-width: 600px;
        text-align: left;
        color: $error-color;
        font-size: 0.8rem;
    }

    .input-group {
        margin-top: 20px;
        display: flex;
        width: 100%;
        max-width: 600px;

        .input-text-field {
            padding: 10px;
            width: 75%;
            max-width: 450px;
            border: 1px solid $border-color;
            border-top-left-radius: 8px;
            border-bottom-left-radius: 8px;
            border-right: transparent;

            &:focus {
                outline: none;
                border-color: $laybuy-purple;
            }
        }

        .btn {
            width: 25%;
            max-width: 150px;
            border: 1px solid $border-color;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            border-left: transparent;
            text-transform: uppercase;
            font-weight: bold;
            background-color: $laybuy-purple;
            color: #fff;
            cursor: pointer;
            opacity: 1;
            transition: opacity 0.3s ease-in-out;

            &:hover {
                opacity: 0.5;
            }

            &:focus {
                outline: none;
            }

            &:disabled {
                background-color: #c6c6c6;
            }
        }
    }
}
</style>
