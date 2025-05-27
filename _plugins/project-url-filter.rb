module Jekyll
    module ProjectUrlFilter
        def project_url(input)
            input.gsub(/[^0-9A-Za-z]/, '-').gsub(/-{1,}/, '-').delete_suffix('-').delete_prefix('-').downcase
        end
    end
end

Liquid::Template.register_filter(Jekyll::ProjectUrlFilter)