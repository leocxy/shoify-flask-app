# ============= PocketSquare GWP Settings =============
# this script only apply the discount to the gift product
# add/remove the free gift product will handle by the shopify Checkout UI extension
# if you have any question or issue, please contact dev@pocketsquare.co.nz
# Please don't modify the script unless you know what are you doing.
# Author: Leo Chen <leo@pocketsquare.co.nz>
PS_GWP_CONFIGS = {
    "enable" => {% if enable %}true{% else %}false{% endif %},
    "debug" => false,
    "test" => false,
    "target" => {{ target.pid }},
    "message" => "{{ message }}",
    "secret_number" => {{ secret_number }},
    "key" => "_gwp_hash_str",
}


class PocketSquareGWP
    attr_accessor :configs
    attr_accessor :items

    def initialize(configs, items)
        @items = items
        @configs = configs
    end

    def debug(item, key, value)
        if @configs['debug'] && item
            props = item.properties == nil ? Hash.new : item.properties
            props['_gwp_' + key] = value
            item.change_properties(props, {message: 'Debug'})
        end
    end

    def generate_hash_str(pid, vid)
        hash_str = ('1' + pid.to_s.split('').last(10).join('')).to_i
        hash_str += (@configs['secret_number'].to_s + vid.to_s.split('').last(5).join('')).to_i
        return '0x' + (hash_str / @configs['secret_number']).floor().to_s(16)
    end

    def inject_test_data()
        return unless @configs['test'] and @configs['debug']
        @items.each do | item |
            pid = item.variant.product.id
            vid = item.variant.id
            hash_str = self.generate_hash_str(pid, vid)
            props = item.properties == nil ? Hash.new : item.properties
            props[@configs['key']] = hash_str
            item.change_properties(props, {message: 'Debug'})
            self.debug(item, 'test', 'inject test data!')
        end
    end

    def apply_discount()
        return unless @configs['enable'] == true
        @items.each do | item |
            pid = item.variant.product.id
            vid = item.variant.id
            next unless pid == @configs['target'] and item.properties != nil
            props = item.properties
            next unless props.key?(@configs['key'])
            # apply the discount
            if props[@configs['key']] == self.generate_hash_str(pid, vid)
                if item.line_price.cents > 0
                    item.change_line_price(Money.zero(), {message: @configs['message']})
                end
            else
                self.debug(item, 'error', 'hash str not match!')
            end
        end
    end

    def run()
        self.inject_test_data()
        self.apply_discount()
    end

end

CAMPAIGNS = [
    PocketSquareGWP.new(PS_GWP_CONFIGS, Input.cart.line_items),
].freeze.each do | campaign |
    campaign.run()
end

Output.cart = Input.cart