<template>
    <div v-if="error" class="Polaris-Labelled__Error">
        <div class="Polaris-Labelled__errorIcon">
            <span class="Polaris-Icon">
                <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm-1-8h2V6H9v4zm0 4h2v-2H9v2z" fill="#31373D" fill-rule="evenodd"/></svg>
            </span>
            {{ error }}
        </div>
    </div>
</template>

<script>
    export default {
        name: "AlertIcon",
        data: () => ({}),
        props: {
            error: {type: String}
        }
    }
</script>

<style lang="scss">
    .Polaris-Labelled__errorIcon {
        display: flex;
        align-items: center;
        .Polaris-Icon {
            display: inline-block;
            margin: 0 5px 0 0;
        }
    }

</style>
