<template>
    <transition name="fade">
        <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-container">
                    <div class="modal-header">
                        <slot name="header">Default Header</slot>
                    </div>
                    <div class="modal-body">
                        <slot name="body">Default Body</slot>
                    </div>
                    <div class="modal-footer">
                        <slot name="footer">
                            Default Footer
                        </slot>
                    </div>
                </div>
            </div>
        </div>
    </transition>
</template>

<script>
    export default {
        name: "Modal",
        data: () => ({}),
        methods: {}
    }
</script>

<style lang="scss">
    .modal-mask {
        position: fixed;
        z-index: 100;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(244, 246, 248, .7);
        display: table;

        .modal-wrapper {
            display: table-cell;
            vertical-align: middle;
        }

        .modal-container {
            width: 500px;
            margin: 0 auto;
            padding: 20px 30px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
        }

        .modal-header {
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.33);

            h3 {
                margin-top: 0;
                font-weight: bold;
            }
        }

        .modal-body {
            margin: 20px 0;
        }

        .modal-default-button {
            float: right;
        }
    }

    .fade-enter-active,
    .fade-leave-active {
        transition: opacity .5s ease;
    }

    .fade-enter,
    .fade-leave-to {
        opacity: 0;
    }
</style>