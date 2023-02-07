# ============= PocketSquare GWP Settings =============
# this script only apply the discount to the gift product
# if not qualify, based on the `force` variable, free gift product will be remove
# if `force` is true, the free gift product will be remove
# if `force` is false, the gift product will be remove when the price is zero dollar
# the discount for gift product only apply when it is quality
# if you have any question or issue, please contact dev@pocketsquare.co.nz
# Please don't modify the script unless you know what are you doing.
# Author: Leo Chen <leo@pocketsquare.co.nz>
PS_GWP_CONFIGS = {
    "debug" => false,
    "test" => false,
    # generate config
    "enable" => {% if enable %}true{% else %}false{% endif %},
    "force" => {% if force_remove %}true{% else %}false{% endif %},
    "method" => {{ method }},
    "value" => {{ value }},
    "pre_requirements" => [{% for item in pre_requirements %}{{ item.pid}}{% if loop.last %}{% else %},{% endif %}{% endfor %}],
    "target" => {{ target.pid }},
    "message" => "{{ message }}",
    "secret_number" => {{ secret_number }},
    "key" => "{{ attr_key }}",
}


class PocketSquareGWP
    attr_accessor :configs
    attr_accessor :items
    attr_accessor :qualify

    def initialize(configs, items)
        @items = items
        @configs = configs
        @qualify = false
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

    def check_qualify()
        @configs['method'] == 1 ? self._check_quantity() : self._check_threshold()
    end

    def remove_gift_product()
        return unless !@qualify
        @configs['force'] ? self._force_remove() : self._smart_remove()
    end

    def apply_discount()
        return unless @configs['enable'] == true and @qualify == true
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
        # qualify items
        self.check_qualify()
        # remove gift product
        self.remove_gift_product()
        self.apply_discount()
    end

    def _check_quantity()
        quantity = 0
        @items.each do | item |
            if @configs['pre_requirements'].include? item.variant.product.id
                quantity += item.quantity
            end
        end
        @qualify = quantity >= @configs['value']
    end

    def _check_threshold()
        amount = 0
        @items.each do | item |
            if @configs['pre_requirements'].include? item.variant.product.id
                amount += item.line_price.cents
            end
        end
        @qualify = amount >= @configs['value']
    end

    def _force_remove()
        @items.delete_if { | item | @configs['target'] == item.variant.product.id }
    end

    def _smart_remove()
        @items.delete_if do | item |
            if @configs['target'] == item.variant.product.id
                item.line_price.cents == 0
            end
            false
        end
    end
end

CAMPAIGNS = [
    PocketSquareGWP.new(PS_GWP_CONFIGS, Input.cart.line_items),
].freeze.each do | campaign |
    campaign.run()
end

Output.cart = Input.cart